import glob
from typing import List, Tuple, Dict
import os

from IHtmlComparator import IHtmlComparator
from difflib_Differ import DifflibDiffer
from difflib_HtmlDiff import DifflibHtmlDiff
from HtmlTreeDiff import HtmlTreeDiff
from HtmlTreeDiff2 import HtmlTreeDiff2
from XmlDiffText import XmlDiffText
from DiffMatchPatch import DiffMatchPatch

class Test:
    _old: str = None
    _new: str = None

    def __init__(self, name: str, old_file: str, new_file: str):
        self.name = name
        self.old_file = old_file
        self.new_file = new_file

    def old(self):
        if self._old is None:
            with open(self.old_file, "r") as f:
                self._old = f.read()
        return self._old

    def new(self):
        if self._new is None:
            with open(self.new_file, "r") as f:
                self._new = f.read()
        return self._new

    def __str__(self):
        return self.name



def get_test_files() -> List[str]:
    return glob.glob("test_html/*.html")

def group_test_files(files: List[str]) -> List[Test]:
    result = {}
    for file in files:
        filename = file.replace("test_html\\", "").replace("_new.html", "").replace("_old.html", "")
        if result.get(filename) is None:
            result[filename] = {}
        if file.endswith("new.html"):
            result[filename]["new"] = file
        else:
            result[filename]["old"] = file

    tests = []

    for t in result:
        tests.append(Test(t, result[t]["old"], result[t]["new"]))

    return tests


def get_test(tests: List[Test], name: str) -> Test:
    return list(filter(lambda t: t.name == name, tests))[0]

def get_testers() -> List[IHtmlComparator]:
    return [
        DifflibDiffer(),
        DifflibHtmlDiff(),
        HtmlTreeDiff(),
        HtmlTreeDiff2(),
        XmlDiffText(),
        DiffMatchPatch()
    ]


def run_test(tester: IHtmlComparator, test: Test):
    result = tester.compare(test.old(), test.new())

    result_dir = os.path.join("test_results", str(tester))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    result_filename = os.path.join(result_dir,  str(test) + ".html")
    with open(result_filename, "w+") as f:
        f.write(result)

    changes = tester.mark_changes(test.old(), test.new())
    if changes:
        changes_filename = os.path.join(result_dir, str(test) + ".changes.html")
        with open(changes_filename, "w+") as f:
            f.write(changes)

    diffs = tester.extract_differences(result)
    if diffs:
        print(str(tester), test.name)
        print(diffs)

def main():
    files = get_test_files()
    tests = group_test_files(files)

    for tester in get_testers():
        for test in tests:
            run_test(tester, test)



if __name__ == '__main__':
    main()


