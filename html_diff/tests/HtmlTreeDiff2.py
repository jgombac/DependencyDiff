from IHtmlComparator import IHtmlComparator
from HtmlUtils import *
from typing import List

from htmltreediff2.diff_html import diff

class HtmlTreeDiff2(IHtmlComparator):

    def compare(self, old: str, new: str):
        old, new = self.preprocess(old, new)

        result = diff(old, new, cutoff=0.5, pretty=True)

        result = normalize_html(result)

        # remove all <del>
        for tag in result(["del"]):
            tag.extract()

        # mark all <ins> with attribute
        for tag in result(["ins"]):
            for child in tag.find_all(recursive=False):
                child["diff-changed"] = "True"
            tag.replaceWithChildren()

        # replace custom <text-node> with its text and mark parent changed
        for tag in result(["text-node"]):
            if tag.has_attr("diff-changed"):
                tag.parent["diff-changed"] = tag["diff-changed"]
            tag.replaceWith(tag["text-value"])

        self.set_style(result)

        return result.prettify()

    def extract_differences(self, html: str) -> List[str]:
        xpaths = []
        soup = normalize_html(html)
        for element in soup.find_all(attrs={"diff-changed": "True"}):
            xpaths.append(get_xpath(element))
        return xpaths

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
        old, new = super(HtmlTreeDiff2, self).preprocess(old, new)
        old, new = old.prettify(), new.prettify()
        return old, new


    def __str__(self):
        return "HtmlTreeDiff2"

