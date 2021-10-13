from database.Database import get_session, Commit, Page, PageContent, PageDiff, Project, Diff as DbDiff, Action
from project.Config import Config
from project.Git import Git
from html_diff.Compare import Compare
from crawler.Crawler import Crawler
from project.ProjectSetup import ProjectSetup
import crawler.Url as Url
import Constants

class Diff:
    projects = {}

    def __init__(self):
        self.db = get_session()

    def diff(self):
        is_set = self.setup()
        while is_set:
            success = self.compare_pages()
            if success:
                self.project_config.commit_diffed(self.old.hash)
            is_set = self.setup()

    def setup(self):
        self.project_config = Config.get_result_project_config()
        if not self.project_config:
            return False

        print("Config:", self.project_config.project_name)

        self.project = Project.get_or_create(self.db, self.project_config.project_name)
        self.git = Git(self.project_config)

        self.commits = []
        current = None
        for x in self.git.get_relevant_commits(self.project_config.min_changes):
            # if x.hexsha in self.project_config.diffed_commits:
            #     current = x.hexsha
            if x.hexsha in self.project_config.processed_commits and x.hexsha not in self.project_config.diffed_commits:
                self.commits.append(x.hexsha)

        # if current is not None:
        #     self.commits.insert(0, current)

        if not self.commits:
            return False

        self.old, self.new = self.set_next_commits()
        if not self.old or not self.new:
            return False

        return True


    def set_next_commits(self):
        for i in range(len(self.commits) - 1):
            old = Commit.get(self.db, self.project_config.project_name, self.commits[i])
            if old:
                for j in range(i + 1, len(self.commits)):
                    new = Commit.get(self.db, self.project_config.project_name, self.commits[j])
                    if new:
                        return old, new


    def compare_pages(self):
        success = self.setup_project(self.old.hash)
        if not success:
            print(f"failed diff deploying {self.old.hash}")
            return
        success = self.setup_project(self.new.hash)
        if not success:
            print(f"failed diff deploying {self.new.hash}")
            return

        for old in self.old.pages:
            for new in self.new.pages:
                if new.url == old.url:
                    print("diff pages: ", new.url, old.url)
                    old_crawler = None
                    new_crawler = None
                    old_content = old.contents[0].content if len(old.contents) > 0 else ""
                    new_content = new.contents[0].content if len(new.contents) > 0 else ""

                    exists = PageDiff.exists(self.db, old.id, new.id)

                    if not exists:
                        compare_result = Compare.compare(old_content, new_content)
                        if compare_result:
                            PageDiff.get_or_create(self.db, old.id, new.id, compare_result)

                            element_diff = Compare.extract_differences(compare_result)

                            if element_diff:
                                old_crawler = Crawler(
                                    Page.get_or_create(self.db, self.project_config.project_name, self.old.hash,
                                                       Url.clean_url(Constants.DOCKER_URL)), self.projects[self.old.hash].port)
                                new_crawler = Crawler(
                                    Page.get_or_create(self.db, self.project_config.project_name, self.new.hash,
                                                       Url.clean_url(Constants.DOCKER_URL)), self.projects[self.new.hash].port)

                                old_crawler.visit_page(old, self.project_config)
                                new_crawler.visit_page(new, self.project_config)

                                for element in element_diff:
                                    old_diff = old_crawler.screenshot(element)
                                    new_diff = new_crawler.screenshot(element)
                                    DbDiff.get_or_create(self.db, old.id, new.id, element, old_diff[1], new_diff[1], old_diff[0], new_diff[0])


                    if old_crawler is None:
                        old_crawler = Crawler(
                            Page.get_or_create(self.db, self.project_config.project_name, self.old.hash,
                                               Url.clean_url(Constants.DOCKER_URL)), self.projects[self.old.hash].port)
                    if new_crawler is None:
                        new_crawler = Crawler(
                            Page.get_or_create(self.db, self.project_config.project_name, self.new.hash,
                                               Url.clean_url(Constants.DOCKER_URL)), self.projects[self.new.hash].port)


                    visited = False
                    for old_action in self.windowed_query(old.actions, Action.id, 1000):
                        for new_action in self.windowed_query(new.actions, Action.id, 10):
                            if old_action.element == new_action.element and old_action.type == new_action.type:
                                old_action_content = old_action.content
                                new_action_content = new_action.content

                                if old_content != old_action_content or new_content != new_action_content:
                                    exists = DbDiff.exists(self.db, old.id, new.id, new_action.id)
                                    if not exists:
                                        compare_result = Compare.compare(old_action_content, new_action_content)
                                        if compare_result:
                                            element_diff = Compare.extract_differences(compare_result)

                                            if element_diff:
                                                old_crawler.visit_and_action(old, old_action, self.project_config)
                                                new_crawler.visit_and_action(old, new_action, self.project_config)
                                                for element in element_diff:
                                                    old_diff = old_crawler.screenshot(element)
                                                    new_diff = new_crawler.screenshot(element)
                                                    DbDiff.get_or_create(self.db, old.id, new.id, element, old_diff[1],
                                                                         new_diff[1], old_diff[0], new_diff[0], new_action.id)

        return True

    def windowed_query(self, q, column, windowsize):
        """"Break a Query into chunks on a given column."""

        single_entity = q.is_single_entity
        q = q.add_column(column).order_by(column)
        last_id = None

        while True:
            subq = q
            if last_id is not None:
                subq = subq.filter(column > last_id)
            chunk = subq.limit(windowsize).all()
            if not chunk:
                break
            last_id = chunk[-1][-1]
            for row in chunk:
                if single_entity:
                    yield row[0]
                else:
                    yield row[0:-1]

    def setup_project(self, version: str) -> bool:
        project = self.deploy_version(version)
        if project is not None:
            self.projects[version] = project
            return True
        return False

    def deploy_version(self, version: str):
        project = ProjectSetup(self.project_config, version)
        success = project.setup()
        if success:
            return project

if __name__ == '__main__':
    diff = Diff()
    diff.diff()
    print("")


