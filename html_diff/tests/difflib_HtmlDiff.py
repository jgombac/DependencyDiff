from IHtmlComparator import IHtmlComparator
from HtmlUtils import *

import difflib

class DifflibHtmlDiff(IHtmlComparator):

    def compare(self, old: str, new: str):
        old, new = self.preprocess(old, new)
        diff = difflib.HtmlDiff()

        return diff.make_file(old, new)

    def preprocess(self, old: str, new: str):
        old, new = super(DifflibHtmlDiff, self).preprocess(old, new)
        old, new = old.prettify().splitlines(), new.prettify().splitlines()
        return old, new

    def __str__(self):
        return "DifflibHtmlDiff"

