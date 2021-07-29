from typing import List, Dict

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
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed
from time import sleep
import threading

lock = threading.Lock()

class CrawlingOrchestrator:
    project_config: ProjectConfig = None
    git: Git = None
    versions: List[str] = []
    projects: Dict[str, ProjectSetup] = {}
    crawlers: Dict[str, Crawler] = {}


    def __init__(self, max_workers=1):
        self.max_workers = max_workers
        db = get_session()
        #truncate_db(db)
        self.project_config = Config.get_next_project_config()
        print("Config:", self.project_config.project_name)
        self.set_git(db)

    def run(self):
        self.run_workers(self.max_workers)

    def run_single(self):
        for x in self.git.get_next_commit(self.project_config):
            self.crawl_next(x)

    def set_git(self, db: Session):
        self.git = Git(self.project_config)
        commits = self.git.clone_relevant_commits(self.project_config)
        print("Number of commits:", len(commits))
        for commit in commits:
            Commit.get_or_create(db, self.project_config.project_name, commit.hexsha)

    def setup_project(self, version: str, db: Session) -> bool:
        project = self.deploy_version(version)
        if project is not None:
            self.projects[version] = project
            page = Page.get_or_create(db, self.project_config.project_name, version, Url.clean_url(Constants.DOCKER_URL))
            self.crawlers[version] = Crawler(page, self.projects[version].port)
            return True
        return False

    def deploy_version(self, version: str) -> ProjectSetup:
        project = ProjectSetup(self.project_config, version)
        success = project.setup()
        if success:
            print("Deployed version:", project.tag)
            return project
        else:
            print("Failed deploying version", project.tag)
            self.project_config.commit_failed(project.tag)

    def get_next_page(self, version: str, db: Session) -> Page:
        return Page.get_next(db, self.project_config.project_name, version)

    def crawl(self, version: str):

        db = get_session()
        build = self.setup_project(version, db)

        if not build:
            self.project_config.current_commits.remove(version)
            return False

        page = self.get_next_page(version, db)

        while page:

            self.crawlers[version].get_page(db, page, self.project_config, version)

            page = self.get_next_page(version, db)

        self.project_config.commit_success(version)


    def crawl_next(self, version):
        with lock:
            self.project_config.current_commits.append(version)
        print(f"{threading.currentThread().ident} Will crawl {version}")
        self.crawl(version)
        return True

    def run_workers(self, num):
        with ThreadPoolExecutor(max_workers=num) as executor:
            results = []
            for x in self.git.get_next_commit(self.project_config):
                results.append(executor.submit(self.crawl_next, x))
                sleep(1)
            for future in as_completed(results):
                print(future.result())







if __name__ == '__main__':
    orch = CrawlingOrchestrator(4)
    #orch.run_single()
    orch.run()


