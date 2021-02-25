import requests
from selenium.common.exceptions import TimeoutException


from utils import *
import utils as Utils
import url_helper as Url

class Page:

    def __init__(self, url, visited=False):
        self.url = url
        self.visited = visited


class Crawler:

    urls = dict()

    def __init__(self, url):
        self.domain = Url.get_domain(url)
        self.base_url = Url.clean_url(url)
        self.urls[self.base_url] = Page(self.base_url)
        self.browser = Utils.get_browser()

    def crawl(self, url):
        try:
            self.browser.get(url)
            self.extract_links()
            content = self.browser.page_source

        except TimeoutException as te:
            print(f"GET Timeout: {url}")
            return

        self.mark_visited(url)

        return content

    def mark_visited(self, url):
        url = self.urls.get(url)
        if url is None:
            self.urls[url] = Page(url, True)
        else:
            url.visited = True

    def extract_links(self):
        initial_urls = Url.extract_urls(self.base_url, self.browser.page_source)
        links = Url.prune_urls(initial_urls, [self.domain], [])

        for link in links:
            url = self.urls.get(link)
            if url is None:
                self.urls[link] = Page(link)






crawler = Crawler("https://9gag.com/trending")

response = crawler.crawl(crawler.base_url)

print(response)