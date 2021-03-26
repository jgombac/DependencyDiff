import subprocess
import json
from typing import List
import Constants
import os
from ProjectConfig import ProjectConfig


def run_cmd(cmd: str) -> subprocess.CompletedProcess:
    print(cmd)
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def run_ps(cmd: str) -> subprocess.CompletedProcess:
    print(cmd)
    return subprocess.run(["powershell", "-ExecutionPolicy", "Unrestricted", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class ProjectSetup:
    def __init__(self, config: ProjectConfig, tag: str):
        self.project_name: str = config.project_name
        self.dockerfile: List[str] = config.dockerfile
        self.tag: str = tag
        self.image_name: str = self.project_name + ":" + self.tag
        self.project_dir: str = os.path.join(Constants.PROJECTS_DIR, self.project_name + "#" + self.tag)
        self.container_id: str = None
        self.port: str = None

    def setup(self) -> bool:
        self.prepare_docker_file()
        if self.build_docker_image():
            return self.run_container()
        return False

    def teardown(self):
        cmd = "docker stop " + self.container_id
        result = run_cmd(cmd)
        if result.returncode != 0:
            return False

        cmd = "docker rmi " + self.image_name
        result = run_cmd(cmd)
        if result.returncode != 0:
            return False
        return True

    def build_docker_image(self) -> bool:
        cmd = "docker inspect --type=image " + self.image_name
        result = run_cmd(cmd)
        if result.returncode == 0:
            return True
        cmd = "docker build -t {} {}".format(self.image_name, self.project_dir)
        result = run_cmd(cmd)
        if result.returncode == 0:
            return True
        return False

    def run_container(self) -> bool:
        try:
            cmd = 'docker rm $(docker stop $(docker ps -a | findstr "' + self.image_name + '" | %{($_ -split "\s+")[0]}))'
            run_ps(cmd)

            cmd = "docker run -d -p 80 " + self.image_name
            result = run_cmd(cmd)
            if result.returncode != 0:
                return False

            self.container_id = result.stdout.decode().strip()
            cmd = "docker port " + self.container_id
            result = run_cmd(cmd)
            if result.returncode != 0:
                return False
            self.port = result.stdout.decode().split(":")[-1]
            return True
        except Exception:
            return False

    def prepare_docker_file(self):
        destination = os.path.join(self.project_dir, "Dockerfile")
        if os.path.exists(destination):
            return
        with open(destination, "w+") as f:
            for line in self.dockerfile:
                f.write(line + "\n")



if __name__ == '__main__':
    norris = ProjectConfig(os.path.join(Constants.CONFIGS_DIR, "angular-ngrx-chuck-norris.json"), os.path.join(Constants.CONFIGS_DIR, "angular-ngrx-chuck-norris.results.json"))
    project = ProjectSetup(norris, "51294bb93494143b1ee957af81e1028294db939b")
    success = project.setup()
    print(success, project.container_id, project.port)
