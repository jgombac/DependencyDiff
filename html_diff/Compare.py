from HtmlUtils import *
from typing import List, Tuple

from htmltreediff2.diff_html import diff

class Compare:

    @staticmethod
    def compare(old: str, new: str) -> str:
        try:
            old, new = Compare.preprocess(old, new)

            result = diff(old, new, cutoff=0.9, pretty=True)

            result = normalize_html(result)

            # remove all <del>
            for tag in result(["del"]):
                tag.parent["diff-deleted"] = True
                tag.extract()

            #result = normalize_html(result.prettify())

            # mark all <ins> with attribute
            for tag in result(["ins"]):
                for child in tag.find_all(recursive=False):
                    child["diff-changed"] = "True"
                tag.replaceWithChildren()

            #result = normalize_html(result.prettify())

            # replace custom <text-node> with its text and mark parent changed
            for tag in result(["text-node"]):
                if tag.has_attr("diff-changed"):
                    tag.parent["diff-text-changed"] = tag["diff-changed"]
                tag.replaceWith(tag["text-value"])

            #result = normalize_html(result.prettify())

            #Compare.set_style(result)

            return result.prettify()
        except RecursionError as re:
            print(re)
        except Exception as ex:
            print(ex)

    @staticmethod
    def extract_differences(html: str) -> List[str]:
        xpaths = []
        soup = normalize_html(html)
        for element in soup.find_all(attrs={"diff-changed": "True"}):
            xpaths.append(get_xpath(element))
        for element in soup.find_all(attrs={"diff-deleted": "True"}):
            xpaths.append(get_xpath(element))
        for element in soup.find_all(attrs={"diff-text-changed": "True"}):
            xpaths.append(get_xpath(element))
        return list(set(xpaths))

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


