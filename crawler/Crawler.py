import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy.orm import Session

from HtmlUtils import normalize_html
from ProjectConfig import ProjectConfig
from database.Database import Page, PageContent, Action, Event
from Form import Form
from Element import Element
from scripts_helper import *
import configuration as config_helper
from time import sleep
import Url
import Utils
from typing import List, Tuple


def Elements(browser, elements):
    return map(lambda x: Element(browser, x), elements)

def Forms(browser, forms):
    return map(lambda x: Form(browser, x), forms)

class Crawler:

    def __init__(self, page: Page, port: str, headless=True):
        self.port = "".join(port.split())
        self.domain = Url.get_domain(f"{page.url}:{self.port}")
        self.domain_name = Url.get_domain_name(f"{page.url}:{self.port}")
        self.base_url = Url.clean_url(f"{page.url}:{self.port}")
        self.base_page = page
        self.browser = Utils.get_chrome(headless)

    def inject_script(self):
        self.browser.execute_script(get_injected_scripts())

    def check_head(self, url):
        try:

            if "data:image" in url and "base64" in url:
                return False

            request = requests.head(url)

            if request.status_code > 300:
                return False

            content_type = request.headers["Content-Type"].lower()
            return "text/html" in content_type

        except Exception as ex:
            print(ex)
            return False

    def get_page(self, db: Session, page: Page, config: ProjectConfig, version: str) -> str:
        try:

            url = Url.set_port(page.url, self.port)
            print(f"Crawling {url}")
            # print(url, page.url, self.port)
            if page.url == "http://localhost/#/":
                self.mark_visited(db, page)
                return

            # if not self.check_head(url):
            #     self.mark_visited(db, page)
            #     return ""

            self.browser.get(url)
            self.inject_script()

            if config.wait_until_clickable:
                WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, config.wait_until_clickable)))

            sleep(2)

            self.remove_repeatable_elements(config.repeatable_elements, config.leave_repeatable)
            self.extract_links(db, page, config)
            content = self.browser.page_source
            PageContent.get_or_create(db, config.project_name, version, page.url, content)

            self.fill_forms(db, config, version, page)

            self.execute_events(db, page, config, version)

        except TimeoutException as te:
            print(f"GET Timeout: {page.url}:{self.port}")
            self.mark_visited(db, page)
            return
        except Exception as ex:
            print("crawler exception", ex)
            self.mark_visited(db, page)
            return

        self.mark_visited(db, page)

        #self.browser.close()
        return content

    def visit_page(self, page: Page, config: ProjectConfig) -> str:
        try:
            url = Url.set_port(page.url, self.port)

            self.browser.get(url)

            if config.wait_until_clickable:
                WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, config.wait_until_clickable)))

            sleep(2)
            #self.inject_script()
            self.remove_repeatable_elements(config.repeatable_elements, config.leave_repeatable)
            content = self.browser.page_source

        except TimeoutException as te:
            print(f"GET Timeout: {page.url}:{self.port}")
            return
        except Exception as ex:
            print("visit page exception", ex)
            return
        return content

    def visit_and_action(self, page: Page, action: Action, config: ProjectConfig):
        try:
            url = Url.set_port(page.url, self.port)

            self.browser.get(url)

            if config.wait_until_clickable:
                WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, config.wait_until_clickable)))

            sleep(2)
            self.remove_repeatable_elements(config.repeatable_elements, config.leave_repeatable)


            element = Element(self.browser, self.browser.find_element_by_xpath(action.element), action.element, [action.type])

            if action.type != "form":
                element.execute_event(action.type)
            else:
                form = Form(self.browser, self.browser.find_element_by_xpath(action.element))
                definition = self.form_definition(form, config)
                form.fill(definition)
                form.submit()
                sleep(1)

            sleep(2)


        except TimeoutException as te:
            print(f"GET Timeout: {page.url}:{self.port}")
        except Exception as ex:
            print(ex)

    def screenshot(self, xpath: str) -> Tuple[str, str]:
        try:
            element = self.browser.find_element_by_xpath(xpath)
            if element:
                return element.get_attribute("outerHTML"), element.screenshot_as_base64
            return "", ""
        except Exception as e:
            print(xpath, e)
            return "", ""


    def remove_repeatable_elements(self, remove_elements: List[str], leave: int):
        for xpath in remove_elements:
            elements = self.browser.find_elements_by_xpath(xpath)[leave::] # leave first element
            for element in elements:
                self.browser.execute_script("""
                    var element = arguments[0];
                    element.parentNode.removeChild(element);
                    """, element)

    def mark_visited(self, db: Session, page: Page):
        page.visited = True
        db.commit()

    def extract_links(self, db: Session, current_page: Page, config: ProjectConfig):
        initial_urls = Url.extract_urls(self.base_url, self.browser.page_source, config.use_hash)
        links = Url.prune_urls(initial_urls, [self.domain], [], self.port, config.use_hash)

        for link in links:
            page = Page.get_or_create(db, self.base_page.commit.project.name, self.base_page.commit.hash, link)
            current_page.to_page.append(page)

    def event_listeners(self):
        return self.browser.execute_script(get_events_accessor())

    def execute_events(self, db: Session, page: Page, config: ProjectConfig, version: str):
        retry = False

        processed = [] + config.skip_xpath


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
                try:
                    Event.get_or_create(db, config.project_name, version, page.url, element.get_xpath(), event)

                    original_content = self.browser.page_source
                    executed = element.execute_event(event)

                    if executed:
                        sleep(1)

                        content = self.browser.page_source
                        print(element.get_xpath(), event)

                        Action.get_or_create(db, config.project_name, version, page.url, content, element.get_xpath(), event)

                        self.visit_page(page, config)

                    content = self.browser.page_source
                    if not executed and content != original_content:
                        self.visit_page(page, config)

                except Exception as ex:
                    print(ex)
            processed.append(element.xpath)

            element = get_next_listener(self)
        return processed

    def get_forms(self):
        return Forms(self.browser, self.browser.find_elements_by_tag_name("form"))

    def refresh(self):
        with WebDriverWait(self.browser, 5).until((self.page_has_loaded())):
            self.browser.get(self.browser.current_url)
        self.inject_script()


    def fill_forms(self, db: Session, config: ProjectConfig, version: str, page: Page):
        forms = list(self.get_forms())
        if not forms:
            return

        for form in forms:
            if self.form_already_filled(db, config, version, page, form.xpath):
                continue

            if not self.should_fill_form(form):
                continue

            definition = self.form_definition(form, config)
            form.fill(definition)
            form.submit()

            sleep(3)

            content = self.browser.page_source
            Action.get_or_create(db, config.project_name, version, page.url, content, form.xpath, "form")
            self.visit_page(page, config)



    def form_definition(self, form: Form, config: ProjectConfig):
        return next(filter(lambda x: x["xpath"] == form.xpath, config.forms), None)


    def wait_for_page_load(self, timeout=10):
        old_page = self.browser.find_element_by_tag_name('html')
        WebDriverWait(self.browser, timeout).until(staleness_of(old_page))

    def page_has_loaded(self):
        page_state = self.browser.execute_script('return document.readyState;')
        return page_state == 'complete'

    def form_already_filled(self, db: Session, config: ProjectConfig, version: str, page: Page, xpath: str) -> bool:
        return Action.get(db, config.project_name, version, page.url, "", xpath, "form")

    def should_fill_form(self, form: Form) -> bool:
        try:
            for child in form.children:
                tag = child().tag_name
                if tag == "input":
                    type = child().get_attribute("type")
                    if type in ["text", "email", "password"]:
                        return True
            return False
        except Exception as ex:
            return False






if __name__ == '__main__':
    get_injected_scripts()
    #crawler = Crawler("http://localhost:8080")

    # crawler = Crawler("https://9gag.com")
    #
    # response = crawler.crawl(crawler.base_url)


    #crawler.fill_forms()
    #crawler.refresh()

    # results = crawler.execute_events()

