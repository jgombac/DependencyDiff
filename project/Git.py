from git import Repo, Commit
import os
from typing import List
from ProjectConfig import ProjectConfig
import Constants

class CommitPair:
    def __init__(self, old: str, new: str):
        self.old = old
        self.new = new

class Git:

    def __init__(self, config: ProjectConfig):
        self.remote = config.repository
        self.local = os.path.join(Constants.PROJECTS_DIR, config.project_name)
        self.latest_local = self.local + "#latest"

        if os.path.exists(self.latest_local):
            self.repo = Repo(self.latest_local)
        else:
            self.repo = Repo.clone_from(self.remote, self.latest_local)

        self.repo.remotes.origin.pull()

    def clone_relevant_commits(self, commits: List[Commit] = None):
        if commits is None:
            commits = self.get_relevant_commits()

        for commit in commits:
            local_path = self.local + "#" + commit.hexsha
            if not os.path.exists(local_path):
                repo = Repo.clone_from(self.remote, local_path)
                repo.git.checkout(commit.hexsha)


    def get_relevant_commits(self) -> List[Commit]:
        commits = self.repo.iter_commits()
        relevant = []
        for commit in commits:
            if any([self.is_file_relevant(filename) for filename in commit.stats.files]):
                relevant.append(commit)

        return relevant

    def get_next_commits(self, config: ProjectConfig) -> CommitPair:
        relevant = self.get_relevant_commits()
        for i in range(0, len(relevant) - 1):
            tag = relevant[i].hexsha
            if not tag in config.processed_commits and not tag in config.failed_commits:
                return CommitPair(tag, relevant[i+1].hexsha)


    @staticmethod
    def is_file_relevant(filename: str) -> bool:
        return filename.endswith(".ts") or \
               filename.endswith(".html") or \
               filename.endswith(".js")
