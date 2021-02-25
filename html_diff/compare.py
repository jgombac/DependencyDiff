import difflib

from diff_match_patch import diff_match_patch

from bs4 import BeautifulSoup, NavigableString, Tag

import test_data as t


# def compare(html1, html2):
#     diff = difflib.Differ()
#     return diff.compare(html1.splitlines(), html2.splitlines())

# def extract_differences(diffs):
#     result = {
#         "-": [],
#         "+": []
#     }
#     for diff in diffs:
#         if diff.startswith("-"):
#             result["-"].append(diff[2:])
#         elif diff.startswith("+"):
#             result["+"].append(diff[2:])
#     return result

def normalize_angular(html):
    return html.replace("*", "asteriks-")

def normalize_html(html):
    html = normalize_angular(html)
    return BeautifulSoup(html, "lxml")



# def get_structure(soup):
#
#     def taggify(soup):
#         for tag in soup:
#             if isinstance(tag, Tag):
#                 yield "<{}>{}</{}>".format(tag.name, "".join(taggify(tag)), tag.name)
#
#     return normalize_html("".join(taggify(soup)))


def delete_displayed_text(soup):
    new_children = []
    for child in soup.contents:
        if not isinstance(child, NavigableString):
            new_children.append(delete_displayed_text(child))
    soup.contents = new_children
    return soup


# def get_diff(html1, html2):
#     html1 = normalize_html(html1)
#     html2 = normalize_html(html2)
#
#     html1 = delete_displayed_text(html1)
#     html2 = delete_displayed_text(html2)
#
#     comparison = compare(html1.prettify(), html2.prettify())
#
#     return extract_differences(comparison)


def generate_differences(old_html, new_html):
    dmp = diff_match_patch()
    diffs = dmp.diff_main(old_html, new_html)
    return dmp.diff_prettyHtml(diffs)



def mark_changed(differences, new_html):
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

    new_html_lines = normalize_html(new_html).prettify().splitlines()

    return [(i, new_html_lines[i]) for i in inserted_lines_num]




old_html = normalize_html(t.t1)
new_html = normalize_html(t.t2)

diffs = generate_differences(old_html.prettify(), new_html.prettify())
changes = mark_changed(diffs, new_html.prettify())
print(changes)

elements = new_html.find_all(True)

for i, line in changes:
    element = elements[i]
    element["data-changed"]= "Added"

print(new_html.prettify())

