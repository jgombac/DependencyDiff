import subprocess
from typing import List, Dict
import json
from test_data import *

class SemanticException(Exception):
    def __init__(self, semantic_error: subprocess.CompletedProcess):
        self.message = "\nCommand: {}\nMessage: {}".format(semantic_error.args, semantic_error.stderr)

    def __str__(self):
        return self.message

def run_semantic(workdir: str, filenames: List[str]) -> Dict:
    docker_image = "docker.pkg.github.com/github/semantic/semantic"
    cmd = "docker run -v {}:/workspace {} parse --json ".format(workdir, docker_image)
    for filename in filenames:
        cmd += "/workspace/{} ".format(filename)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        return json.loads(result.stdout.decode().strip())
    raise SemanticException(result)

if __name__ == '__main__':
    data = run_semantic(test_workdir, test_files)
    print(data)