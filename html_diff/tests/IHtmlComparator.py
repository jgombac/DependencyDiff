from HtmlUtils import *
from typing import Tuple, List
from bs4 import BeautifulSoup


class IHtmlComparator:

    def compare(self, old: str, new: str) -> str:
        pass

    def mark_changes(self, old: str, new: str) -> str:
        pass

    def extract_differences(self, html: str) -> List[str]:
        pass

    def preprocess(self, old: str, new: str) -> Tuple[BeautifulSoup, BeautifulSoup]:
        return normalize_html(old), normalize_html(new)

    def __str__(self):
        return "IHtmlComparator"