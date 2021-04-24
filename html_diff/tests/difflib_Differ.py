from IHtmlComparator import IHtmlComparator
from HtmlUtils import *

import difflib

class DifflibDiffer(IHtmlComparator):

    def compare(self, old: str, new: str):
        old, new = self.preprocess(old, new)
        diff = difflib.Differ().compare(old, new)

        result = ""
        for line in diff:
            result += line + "\n"

        return result

    def preprocess(self, old: str, new: str):
        old, new = super(DifflibDiffer, self).preprocess(old, new)
        old, new = old.prettify().splitlines(), new.prettify().splitlines()
        return old, new

    def __str__(self):
        return "DifflibDiffer"

