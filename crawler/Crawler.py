import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy.orm import Session

from HtmlUtils import normalize_html
from ProjectConfig import ProjectConfig
from Database import Page, PageContent
from Form import Form
from Element import Element
from scripts_helper import *
import configuration as config
from time import sleep
import Url
import Utils
from typing import List


def Elements(browser, elements):
    return map(lambda x: Element(browser, x), elements)

def Forms(browser, forms):
    return map(lambda x: Form(browser, x), forms)

class Crawler:

    def __init__(self, page: Page, port: str):
        self.port = port
        self.domain = Url.get_domain(f"{page.url}:{port}")
        self.domain_name = Url.get_domain_name(f"{page.url}:{port}")
        self.base_url = Url.clean_url(f"{page.url}:{port}")
        self.browser = Utils.get_chrome()
        self.base_page = page

    def inject_script(self):
        self.browser.execute_script(get_injected_scripts())

    def crawl(self, db: Session):
        page = Page.get_next(db, self.base_page.commit.project.name, self.base_page.commit.hash)
        while page:
            self.get_page(db, page)
            page = Page.get_next(db, self.base_page.commit.project.name, self.base_page.commit.hash)

    def get_page(self, db: Session, page: Page, config: ProjectConfig):
        try:
            url = Url.set_port(page.url, self.port)
            self.browser.get(url)
            sleep(1)
            self.inject_script()
            self.remove_repeatable_elements(config.repeatable_elements)
            self.extract_links(db)
            content = self.browser.page_source

        except TimeoutException as te:
            print(f"GET Timeout: {page.url}:{self.port}")
            return

        self.mark_visited(db, page)

        return content

    def remove_repeatable_elements(self, remove_elements: List[str]):
        for xpath in remove_elements:
            elements = self.browser.find_elements_by_xpath(xpath)[1::] # leave first element
            for element in elements:
                self.browser.execute_script("""
                    var element = arguments[0];
                    element.parentNode.removeChild(element);
                    """, element)

    def mark_visited(self, db: Session, page: Page):
        page.visited = True
        db.commit()

    def extract_links(self, db: Session):
        initial_urls = Url.extract_urls(self.base_url, self.browser.page_source)
        links = Url.prune_urls(initial_urls, [self.domain], [])

        for link in links:
            Page.get_or_create(db, self.base_page.commit.project.name, self.base_page.commit.hash, link.replace(f":{self.port}", ""))

    def event_listeners(self):
        return self.browser.execute_script(get_events_accessor())

    def execute_events(self):
        retry = False

        processed = [] + config.get_skip_xpaths(self.domain_name)


        def get_next_listener(self):
            listeners = self.event_listeners()
            if len(listeners) == 0:
                sleep(1)
                print("No listeners, retrying...")
                listeners = self.event_listeners()
                if not listeners:
                    return
            for listener in listeners:
                element = Element(self.browser, listener["element"], listener["xpath"], listener["events"])
                if element.xpath not in processed:
                    return element

        element = get_next_listener(self)

        while element is not None:
            for event in element.events:
                element.execute_event(event)
            processed.append(element.xpath)

            element = get_next_listener(self)
        return processed

    def get_forms(self):
        # TODO remove this
        if "9gag.com" in self.domain:
            self.browser.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/button[2]").click()
            self.browser.find_element_by_xpath("/html/body/div[2]/div/header/div/div/div[1]/a[2]").click()

        return Forms(self.browser, self.browser.find_elements_by_tag_name("form"))

    def refresh(self):
        with WebDriverWait(self.browser, 5).until((self.page_has_loaded())):
            self.browser.get(self.browser.current_url)
        self.inject_script()


    def fill_forms(self):
        forms = list(self.get_forms())
        if not forms:
            return
        form = forms[0]
        form.fill()
        form.submit()


    def wait_for_page_load(self, timeout=10):
        old_page = self.browser.find_element_by_tag_name('html')
        WebDriverWait(self.browser, timeout).until(staleness_of(old_page))

    def page_has_loaded(self):
        page_state = self.browser.execute_script('return document.readyState;')
        return page_state == 'complete'






if __name__ == '__main__':
    get_injected_scripts()
    #crawler = Crawler("http://localhost:8080")

    # crawler = Crawler("https://9gag.com")
    #
    # response = crawler.crawl(crawler.base_url)


    #crawler.fill_forms()
    #crawler.refresh()

    # results = crawler.execute_events()

