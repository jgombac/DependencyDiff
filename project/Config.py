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
    def get_next_project_config() -> ProjectConfig:
        configs = Config.get_project_configs()
        for config in configs:
            config_result = config.replace(".json", ".results.json")
            if not os.path.isfile(config_result):
                with open(config_result, "w") as f:
                    f.write('''{
    "done": false,
    "processed_commits": [],
    "failed_commits": []
}''')

            with open(config_result, "r") as f:
                results_content = json.loads(f.read())
                if not results_content["done"]:
                    return ProjectConfig(config, config_result)
