import json
from typing import List

class ProjectConfig:

    def __init__(self, config_file: str, results_file: str):
        self.config_file = config_file
        self.results_file = results_file

        with open(config_file, "r") as f:
            config = json.loads(f.read())
        self.project_name: str = config["project_name"]
        self.repository: str = config["repository"]
        self.first_commit: str = config["first_commit"]
        self.use_hash: bool = config["use_hash"]
        self.min_changes: int = config["min_changes"]
        self.dockerfile: List[str] = config["dockerfile"]
        self.wait_until_clickable: str = config["wait_until_clickable"]
        self.skip_xpath: List[str] = config["skip_xpath"]
        self.forms: List = config["forms"]
        self.repeatable_elements: List[str] = config["repeatable_elements"]
        self.leave_repeatable: int = config["leave_repeatable"]
        self.clean_text_elements: List[str] = config["clean_text_elements"]

        with open(results_file, "r") as f:
            results = json.loads(f.read())

        self.finished: bool = results["done"]
        self.processed_commits: List[str] = results["processed_commits"]
        self.failed_commits: List[str] = results["failed_commits"]
        self.diffed_commits: List[str] = results["diffed_commits"]
        self.current_commits = []


    def commit_failed(self, version: str):
        self.failed_commits.append(version)
        self.save_results()

    def commit_success(self, version: str):
        self.processed_commits.append(version)
        self.save_results()

    def project_finished(self):
        self.done = True
        self.save_results()

    def commit_diffed(self, version: str):
        self.diffed_commits.append(version)
        self.save_results()

    def save_results(self):
        value = json.dumps({
            "done": self.finished,
            "processed_commits": self.processed_commits,
            "failed_commits": self.failed_commits,
            "diffed_commits": self.diffed_commits
        }, indent=2, sort_keys=True)
        with open(self.results_file, "w") as f:
            f.write(value)

    def __str__(self):
        return str({
            "project_name": self.project_name,
            "repository": self.repository,
            "dockerfile": self.dockerfile,
            "skip_xpath": self.skip_xpath,
            "forms": self.forms,
            "processed_commits": self.processed_commits,
            "repeatable_elements": self.repeatable_elements,
            "clean_text_elements": self.clean_text_elements
        })

