from IHtmlComparator import IHtmlComparator
from HtmlUtils import *

from diff_match_patch import diff_match_patch

class DiffMatchPatch(IHtmlComparator):

    def compare(self, old: str, new: str):
        old, new = self.preprocess(old, new)

        dmp = diff_match_patch()
        diffs = dmp.diff_main(old, new)

        html = normalize_html(dmp.diff_prettyHtml(diffs).replace("<br>", ""))

        for tag in html(["html", "body", "span"]):
            tag.replaceWithChildren()


        return html.prettify().replace("&lt;", "<").replace("&gt;", ">")

        result = ""
        for i, html in diffs:
            if i == 0: # same
                result += html
            elif i == -1: #deleted
                pass
                #result += "<del>{}</del>".format(html)
            elif i == 1: #added
                result += "<ins>{}</ins>".format(html)

        return normalize_html(result).prettify()

    def mark_changes(self, old: str, new: str):
        differences = self.compare(old, new)
        differences = normalize_html(differences)

        for s in differences(["del"]):
            s.extract()

        newlines = 0
        inserted_lines_num = []
        for tag in differences.find_all(True):
            if tag.name == "br":
                newlines += 1
            elif tag.name == "ins":
                inserted_lines_num.append(newlines)

        new_html_lines = normalize_html(new).prettify().splitlines()

        result = ""
        for i in inserted_lines_num:
            result += new_html_lines[i]
        return result


        # return None
        # differences = normalize_html(self.compare(old, new))
        #
        #
        # for s in differences(["del"]):
        #     s.extract()
        #
        # newlines = 0
        # inserted_lines_num = []
        # for tag in differences.find_all(True):
        #     if tag.name == "br":
        #         newlines += 1
        #     elif tag.name == "ins":
        #         inserted_lines_num.append(newlines)
        #
        # new_html = normalize_html(new)
        # new_html_lines = new_html.prettify().splitlines()
        #
        # changes = [(i, new_html_lines[i]) for i in inserted_lines_num]
        # elements = new_html.find_all(True)
        #
        # for i, line in changes:
        #     element = elements[i]
        #     element["data-changed"] = "true"
        #
        # return new_html.prettify()

    def preprocess(self, old: str, new: str):
        old, new = super(DiffMatchPatch, self).preprocess(old, new)
        old, new = old.prettify(), new.prettify()
        return old, new

    def __str__(self):
        return "DiffMatchPatch"
