import json
from typing import List

class ProjectConfig:

    def __init__(self, config_file: str, results_file: str):
        with open(config_file, "r") as f:
            config = json.loads(f.read())
        self.project_name: str = config["project_name"]
        self.repository: str = config["repository"]
        self.dockerfile: List[str] = config["dockerfile"]
        self.skip_xpath: List[str] = config["skip_xpath"]
        self.forms: List = config["forms"]

        with open(results_file, "r") as f:
            results = json.loads(f.read())

        self.processed_commits: List[str] = results["processed_commits"]
        self.failed_commits: List[str] = results["failed_commits"]


    def __str__(self):
        return str({
            "project_name": self.project_name,
            "repository": self.repository,
            "dockerfile": self.dockerfile,
            "skip_xpath": self.skip_xpath,
            "forms": self.forms,
            "processed_commits": self.processed_commits
        })

