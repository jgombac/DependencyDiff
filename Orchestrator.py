from typing import List

from Compare import Compare
import Constants
import glob
import os
from Config import Config
from ProjectConfig import ProjectConfig
from ProjectSetup import ProjectSetup
from Git import Git, CommitPair
from Crawler import Crawler, get_injected_scripts
from database.Database import *
import Url



class Orchestrator:
    project_config: ProjectConfig = None
    git: Git = None
    versions: CommitPair = None
    old_project: ProjectSetup = None
    new_project: ProjectSetup = None
    old_crawler: Crawler = None
    new_crawler: Crawler = None


    def __init__(self):
        self.db = get_session()
        truncate_db(self.db)

    def setup(self):
        self.set_project_config()
        self.set_git()
        self.set_versions()

        build = self.build_projects()
        while not build:
            self.set_versions()
            build = self.build_projects()

        self.set_crawlers()

    def set_project_config(self):
        self.project_config = Config.get_next_project_config()


    def set_git(self):
        self.git = Git(self.project_config)
        commits = self.git.clone_relevant_commits()
        for commit in commits:
            Commit.get_or_create(self.db, self.project_config.project_name, commit.hexsha)


    def set_versions(self):
        self.versions = self.git.get_next_commits(self.project_config)

    def build_projects(self) -> bool:
        self.old_project = self.deploy_version(self.versions.old)
        if self.old_project is None:
            return False
        self.new_project = self.deploy_version(self.versions.new)
        if self.new_project is None:
            return False
        return True

    def deploy_version(self, version: str) -> ProjectSetup:
        project = ProjectSetup(self.project_config, version)
        success = project.setup()
        if success:
            print("Deployed version:", project.tag)
            return project
        else:
            print("Failed deploying version", project.tag)
            self.project_config.failed_commits.append(project.tag)

    def set_crawlers(self):
        old_page = Page.get_or_create(self.db, self.project_config.project_name, self.versions.old, Url.clean_url(Constants.DOCKER_URL))
        new_page = Page.get_or_create(self.db, self.project_config.project_name, self.versions.new, Url.clean_url(Constants.DOCKER_URL))
        self.old_crawler = Crawler(old_page, self.old_project.port)
        self.new_crawler = Crawler(new_page, self.new_project.port)

    def get_next_page_pair(self):
        old_page = None
        new_page = None

        while not old_page and not new_page:
            old_page = Page.get_next(self.db, self.project_config.project_name, self.versions.old)

            if not old_page:
                break

            new_page = Page.get_next(self.db, self.project_config.project_name, self.versions.new, old_page.url)

            if not new_page:
                old_page.visited = True
                self.db.commit()
                old_page = None

        return old_page, new_page


    def crawl(self):

        old_page, new_page = self.get_next_page_pair()

        while old_page and new_page:

            print(f"Crawling {old_page.url}")

            old_content = self.old_crawler.get_page(self.db, old_page, self.project_config)
            new_content = self.new_crawler.get_page(self.db, new_page, self.project_config)

            PageContent.get_or_create(self.db, self.project_config.project_name, self.versions.old, old_page.url, old_content)
            PageContent.get_or_create(self.db, self.project_config.project_name, self.versions.new, new_page.url, new_content)

            compare_result = Compare.compare(old_content, new_content)
            element_diff = Compare.extract_differences(compare_result)

            for element in element_diff:
                Diff.get_or_create(self.db, old_page.id, new_page.id, element)

            old_page, new_page = self.get_next_page_pair()




if __name__ == '__main__':
    orch = Orchestrator()
    orch.setup()
    orch.crawl()
    print("")


