from typing import List
from commandline import run_semantic

class Semantic:
    trees = None

    def __init__(self, workdir: str, filenames: List[str]):
        self.workdir = workdir
        self.filenames = filenames

    def __parse(self):
        return run_semantic(self.workdir, self.filenames)

    def get_trees(self):
        if self.trees:
            return self.trees
        parse_results = self.__parse()
        self.trees = list(filter(lambda tree_list: tree_list.get("tree"), parse_results["trees"]))
        return self.trees


if __name__ == '__main__':
    test_dir = "A:/Development"
    test_files = ["PRPO/prpo-frontend/src/app/professor/professors/professors.component.ts", "PRPO/prpo-frontend/src/app/professor/professor-create/professor-create.component.html"]
    semantic = Semantic(test_dir, test_files)
    print(semantic.get_trees())