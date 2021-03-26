from typing import List
import Constants
import glob
import os
from Config import Config
from ProjectConfig import ProjectConfig
from ProjectSetup import ProjectSetup
from Git import Git, CommitPair
from Crawler import Crawler, get_injected_scripts



class Orchestrator:
    project_config: ProjectConfig = None
    git: Git = None
    versions: CommitPair = None
    old_project: ProjectSetup = None
    new_project: ProjectSetup = None
    old_crawler: Crawler = None
    new_crawler: Crawler = None


    def __init__(self):
        pass

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
        self.git.clone_relevant_commits()

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
        self.old_crawler = Crawler(Constants.DOCKER_URL + ":" + self.old_project.port)
        self.new_crawler = Crawler(Constants.DOCKER_URL + ":" + self.new_project.port)

    def crawl(self):
        content = self.old_crawler.crawl(self.old_crawler.domain)
        print(content)
        content = self.new_crawler.crawl(self.new_crawler.domain)
        print(content)








if __name__ == '__main__':
    orch = Orchestrator()
    orch.setup()
    orch.crawl()
    print("")


