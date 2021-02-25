from bs4 import BeautifulSoup, NavigableString
from lxml import etree, html as h
import test_data as t
from xmldiff import main as xml, actions as a


def normalize_angular(html):
    return html.replace("*", "asteriks-")

def normalize_html(html):
    html = normalize_angular(html)
    return BeautifulSoup(html, "lxml")

def get_xml(soup):
    return etree.tostring(h.fromstring(soup.prettify()))


def delete_displayed_text(soup):
    new_children = []
    for child in soup.contents:
        if not isinstance(child, NavigableString):
            new_children.append(delete_displayed_text(child))
    soup.contents = new_children
    return soup


def diff(before, after):
    before_soup = delete_displayed_text(normalize_html(before))
    after_soup = delete_displayed_text(normalize_html(after))

    left = get_xml(before_soup)
    right = get_xml(after_soup)

    actions = xml.diff_texts(left, right, diff_options={'F': 0.5, 'ratio_mode': 'accurate'})

    actions2 = xml.diff_texts(right, left, diff_options={'F': 0.5, 'ratio_mode': 'accurate'})

    inter = []
    for a in actions:
        for a2 in actions2:
            if hasattr(a, 'node') and hasattr(a2, 'node') and a.node == a2.node:
                inter.append(a)
                break
            elif hasattr(a, 'target') and hasattr(a2, 'target') and a.target == a2.target:
                inter.append(a)
                break




    print(actions)



diff(t.t1, t.t2)

    