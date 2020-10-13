import itertools as it, glob
from typing import List, Optional


def get_workdir_files(workdir: str, project_dir: str, extensions: Optional[List[str]] = None) -> List[str]:
    if not extensions:
        extensions = [".ts"]
    extensions = map(lambda ext: "/**/*" + ext, extensions)
    all_files = it.chain.from_iterable(glob.iglob(workdir + project_dir + ext, recursive=True) for ext in extensions)
    return [file.replace(workdir, "").replace("\\", "/") for file in all_files if not "node_modules" in file]


if __name__ == '__main__':
    test_workdir = "A:/Development"
    project_dir = "/PRPO/prpo-frontend"
    files = get_workdir_files(test_workdir, project_dir, [".html", ".ts"])
    print(files)