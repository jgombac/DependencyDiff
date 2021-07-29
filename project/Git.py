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
    relevant_commits = None

    def __init__(self, config: ProjectConfig):
        self.first_commit = config.first_commit
        self.remote = config.repository
        self.local = os.path.join(Constants.PROJECTS_DIR, config.project_name)
        self.latest_local = self.local + "#latest"

        if os.path.exists(self.latest_local):
            self.repo = Repo(self.latest_local)
        else:
            self.repo = Repo.clone_from(self.remote, self.latest_local)

        self.repo.remotes.origin.pull()

    def clone_relevant_commits(self, config: ProjectConfig, commits: List[Commit] = None, ) -> List[Commit]:
        if commits is None:
            commits = self.get_relevant_commits(config.min_changes)

        for commit in commits:
            local_path = self.local + "#" + commit.hexsha
            if not os.path.exists(local_path):
                print("cloning:", commit.hexsha)
                repo = Repo.clone_from(self.remote, local_path)
                repo.git.checkout(commit.hexsha)
            else:
                print("skipping:", commit.hexsha)
        return commits


    def get_relevant_commits(self, min_changes: int) -> List[Commit]:
        if self.relevant_commits:
            return self.relevant_commits

        commits = self.repo.iter_commits(reverse=True)
        relevant = []
        found_first = True if not self.first_commit else False
        for commit in commits:
            if self.first_commit and commit.hexsha == self.first_commit:
                found_first = True
            if found_first:
                if any([self.is_file_relevant(filename, changes, min_changes) for filename, changes in commit.stats.files.items()]):
                    relevant.append(commit)

        self.relevant_commits = relevant
        return relevant

    def get_next_commit(self, config: ProjectConfig) -> str:
        relevant = self.get_relevant_commits(config.min_changes)
        for commit in relevant:
            if commit.hexsha not in config.processed_commits and \
                            commit.hexsha not in config.failed_commits and \
                            commit.hexsha not in config.current_commits:
                yield commit.hexsha

    def get_next_commits(self, config: ProjectConfig) -> CommitPair:
        relevant = self.get_relevant_commits(config.min_changes)
        for i in range(len(relevant) - 1):
            x = relevant[i]
            if x.hexsha not in config.processed_commits and x.hexsha not in config.failed_commits:
                for j in range(i + 1, len(relevant)):
                    y = relevant[j]
                    if y.hexsha not in config.processed_commits and y.hexsha not in config.failed_commits:
                        return CommitPair(x.hexsha, y.hexsha)



    @staticmethod
    def is_file_relevant(filename: str, changes, min_changes: int) -> bool:
        return (filename.endswith("component.ts") or
                filename.endswith("module.ts") or
               filename.endswith("component.html")) and changes["lines"] >= min_changes

