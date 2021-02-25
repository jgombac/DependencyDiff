import itertools as it, glob
from typing import List, Optional
from test_data import *


def get_workdir_files(workdir: str, project_dir: str, extensions: Optional[List[str]] = None) -> List[str]:
    if not extensions:
        extensions = [".ts"]
    extensions = map(lambda ext: "/**/*" + ext, extensions)
    all_files = it.chain.from_iterable(glob.iglob(workdir + project_dir + ext, recursive=True) for ext in extensions)
    return [file.replace(workdir, "").replace("\\", "/") for file in all_files if not "node_modules" in file]


if __name__ == '__main__':
    files = get_workdir_files(test_workdir, test_project_dir, [".html", ".ts"])
    print(files)