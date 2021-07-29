from database.Database import get_session, Commit, Page, PageContent, PageDiff, Project, Diff as DbDiff, truncate_db
from project.Config import Config
from project.Git import Git
from html_diff.Compare import Compare
from crawler.Crawler import Crawler
from project.ProjectSetup import ProjectSetup
from project.ProjectConfig import ProjectConfig
import crawler.Url as Url
import Constants
from html_diff.Diff import Diff

class FriExample:
    project_name = "fri.uni-lj.si"

    examples = [
        ("20161207132431", "https://web.archive.org/web/20161207132431/http://www.fri.uni-lj.si:80/en/"),
        ("20170129015754", "https://web.archive.org/web/20170129015754/https://www.fri.uni-lj.si/en/"),
        ("20170922110659", "https://web.archive.org/web/20170922110659/https://fri.uni-lj.si/en"),
        ("20171027125058", "https://web.archive.org/web/20171027125058/https://www.fri.uni-lj.si/en")
    ]

    # # old_hash = "20161207132431"
    # # new_hash = "20170129015754"
    # #
    # # old_url = "https://web.archive.org/web/20161207132431/http://www.fri.uni-lj.si:80/en/"
    # # new_url = "https://web.archive.org/web/20170129015754/https://www.fri.uni-lj.si/en/"
    #
    # # old_hash = "20170129015754"
    # # old_url = "https://web.archive.org/web/20170129015754/https://www.fri.uni-lj.si/en/"
    # #
    # # new_hash = "20170922110659"
    # # new_url = "https://web.archive.org/web/20170922110659/https://fri.uni-lj.si/en"
    #
    # old_hash = "20170922110659"
    # old_url = "https://web.archive.org/web/20170922110659/https://fri.uni-lj.si/en"
    # new_hash = "20171027125058"
    # new_url = "https://web.archive.org/web/20171027125058/https://www.fri.uni-lj.si/en"


    def __init__(self):
        db = get_session()
        truncate_db(db)

        config = ProjectConfig("A:/Development/magistrska/DependencyDiff/configs/fri.json", "A:/Development/magistrska/DependencyDiff/configs/fri.results.json")

        for old, new in zip(self.examples, self.examples[1::]):
            self.old_hash, self.old_url = old
            self.new_hash, self.new_url = new

            old_page = Page.get_or_create(db, self.project_name, self.old_hash, "https://www.fri.uni-lj.si/en/")
            old_page.url = self.old_url
            new_page = Page.get_or_create(db, self.project_name, self.new_hash, self.new_url)

            old_crawler = Crawler(old_page, "443")
            new_crawler = Crawler(new_page, "443")

            old_crawler.get_page(db, old_page, config, self.old_hash)
            new_crawler.get_page(db, new_page, config, self.new_hash)

            old_content = old_page.contents[0].content if len(old_page.contents) > 0 else ""
            new_content = new_page.contents[0].content if len(new_page.contents) > 0 else ""

            compare_result = Compare.compare(old_content, new_content)

            if compare_result:
                element_diff = Compare.extract_differences(compare_result)
                for element in element_diff:
                    old_diff = old_crawler.screenshot(element)
                    new_diff = new_crawler.screenshot(element)
                    DbDiff.get_or_create(db, old_page.id, new_page.id, element, old_diff[1], new_diff[1], old_diff[0],
                                         new_diff[0])

            for old_action in old_page.actions:
                for new_action in new_page.actions:
                    if old_action.element == new_action.element and old_action.type == new_action.type:
                        old_action_content = old_action.content
                        new_action_content = new_action.content

                        if old_content != old_action_content or new_content != new_action_content:

                            compare_result = Compare.compare(old_action_content, new_action_content)
                            if compare_result:
                                element_diff = Compare.extract_differences(compare_result)

                                if element_diff:
                                    old_crawler.visit_and_action(old_page, old_action, config)
                                    new_crawler.visit_and_action(new_page, new_action, config)
                                    for element in element_diff:
                                        old_diff = old_crawler.screenshot(element)
                                        new_diff = new_crawler.screenshot(element)
                                        DbDiff.get_or_create(db, old_page.id, new_page.id, element, old_diff[1],
                                                             new_diff[1], old_diff[0], new_diff[0], new_action.id)

            old_page.url = "https://www.fri.uni-lj.si/en/"
            new_page.url = "https://www.fri.uni-lj.si/en/"

            db.commit()


if __name__ == '__main__':
    FriExample()
