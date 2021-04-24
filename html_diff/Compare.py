from HtmlUtils import *
from typing import List, Tuple

from htmltreediff2.diff_html import diff

class Compare:

    @staticmethod
    def compare(old: str, new: str) -> str:
        old, new = Compare.preprocess(old, new)

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
                tag.parent["diff-text-changed"] = tag["diff-changed"]
            tag.replaceWith(tag["text-value"])

        Compare.set_style(result)

        return result.prettify()

    @staticmethod
    def extract_differences(html: str) -> List[str]:
        xpaths = []
        soup = normalize_html(html)
        for element in soup.find_all(attrs={"diff-changed": "True"}):
            xpaths.append(get_xpath(element))
        return xpaths

    @staticmethod
    def set_style(html: BeautifulSoup):
        style = html.new_tag("style")
        style.append(Compare.get_style())
        html.head.insert(0, style)

    @staticmethod
    def get_style() -> str:
        return '''
        [diff-changed], [diff-changed] * {
            background-color: rgba(0, 0, 255, 0.2);
        }
        '''

    @staticmethod
    def preprocess(old: str, new: str) -> Tuple[str, str]:
        return normalize_html(old).prettify(), normalize_html(new).prettify()


