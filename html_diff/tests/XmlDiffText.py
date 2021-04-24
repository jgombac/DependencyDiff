from IHtmlComparator import IHtmlComparator
from HtmlUtils import *
from xmldiff import main as xml, formatting

class XmlDiffText(IHtmlComparator):

    def compare(self, old: str, new: str):
        old, new = self.preprocess(old, new)
        old, new = get_xml(old), get_xml(new)

        diffs = xml.diff_texts(old, new, diff_options={'F': 0.5, 'ratio_mode': 'accurate'})
        diff = xml.diff_texts(old, new, formatter=formatting.XMLFormatter(normalize=formatting.WS_BOTH),
                              diff_options={'F': 0.5, 'ratio_mode': 'accurate'})
        diff = normalize_html(diff)
        self.set_style(diff)

        return diff.prettify()

    def preprocess(self, old: str, new: str):
        old, new = super(XmlDiffText, self).preprocess(old, new)
        #old, new = old.prettify().splitlines(), new.prettify().splitlines()
        return old, new

    def set_style(self, html: BeautifulSoup):
        style = html.new_tag("style")
        style.append(self.get_style())
        html.head.insert(0, style)

    def get_style(self) -> str:
        return '''
        [diff\:replace] {
            background-color: rgba(255, 246, 143, 0.5);
        }
        [diff\:update-attr] {
            background-color: rgba(0, 0, 255, 0.2);
        }
        [diff\:rename] {
            background-color: rgba(0, 0, 255, 0.2);
        }
        [diff\:delete] {
            display: none;
            background-color: rgba(255, 0, 0, 0.5);
        }
        [diff\:insert] {
            background-color: rgba(0, 255, 0, 0.5);
        }
        '''

    def __str__(self):
        return "XmlDiffText"
