from typing import List
import Constants
import glob
import os
from ProjectConfig import ProjectConfig
import json

class Config:

    @staticmethod
    def get_project_configs() -> List[str]:
        return sorted([x for x in glob.glob(Constants.CONFIGS_DIR + "/*.json") if not x.endswith(".results.json")])

    @staticmethod
    def get_result_project_config():
        configs = Config.get_project_configs()
        for config in configs:
            config_result = config.replace(".json", ".results.json")
            if os.path.isfile(config_result):
                with open(config_result, "r") as f:
                    results_content = json.loads(f.read())
                    if len(results_content["processed_commits"]) > len(results_content["diffed_commits"]) + 1:
                        return ProjectConfig(config, config_result)

    @staticmethod
    def get_next_project_config() -> ProjectConfig:
        configs = Config.get_project_configs()
        for config in configs:
            config_result = config.replace(".json", ".results.json")
            if os.path.exists(config_result):

                if not os.path.isfile(config_result):
                    with open(config_result, "w") as f:
                        f.write('''{
        "done": false,
        "processed_commits": [],
        "failed_commits": [],
        "diffed_commits" []
    }''')

                with open(config_result, "r") as f:
                    results_content = json.loads(f.read())
                    if not results_content["done"]:
                        return ProjectConfig(config, config_result)
