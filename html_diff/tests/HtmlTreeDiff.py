from IHtmlComparator import IHtmlComparator
from HtmlUtils import *

from htmltreediff.diff_html import diff

class HtmlTreeDiff(IHtmlComparator):

    def compare(self, old: str, new: str):
        old, new = self.preprocess(old, new)
        result = diff(old, new, cutoff=0.5, pretty=True)


        result = normalize_html(result)

        for tag in result(["del"]):
            tag.extract()

        for tag in result(["ins"]):
            for child in tag.find_all(recursive=False):
                child["diff-changed"] = ""
            tag.replaceWithChildren()

        #self.set_style(result)

        return result.prettify()


    def set_style(self, html: BeautifulSoup):
        style = html.new_tag("style")
        style.append(self.get_style())
        html.head.insert(0, style)

    def get_style(self) -> str:
        return '''
        [diff-changed], [diff-changed] * {
            background-color: rgba(0, 0, 255, 0.2);
        }
        '''


    def preprocess(self, old: str, new: str):
        old, new = super(HtmlTreeDiff, self).preprocess(old, new)
        old, new = old.prettify(), new.prettify()
        return old, new

    def __str__(self):
        return "HtmlTreeDiff"

