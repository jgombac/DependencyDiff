from typing import List
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, \
    StaleElementReferenceException, \
    ElementClickInterceptedException, \
    ElementNotInteractableException


class Element:
    def __init__(self, browser: WebDriver, element: WebElement, xpath: str = None, events: List[str] = list()):
        self.element = element
        self.browser = browser
        self.xpath = xpath if xpath is not None else self.get_xpath()

        self.events = events
        self.performed_events = list()
        self.skipped_events = list()
        self.excepted_events = list()

        self.allowed_hrefs = ["", "#"]

    def mark(self):
        try:
            ActionChains(self.browser).move_to_element(self.get_element()).perform()
            self.browser.execute_script("arguments[0].style.border = '10px solid red'", self.get_element())
        except TimeoutException:
            print("TimeoutException marking element")
        except AttributeError:
            raise

    def click(self):
        self.browser.execute_script("arguments[0].click();", self.get_element())


    def execute_event(self, event: str):
        if not self.is_supported(event) or self.already_tried(event) or self.is_link(event):
            return False
        try:
            if event == "click":
                #self.mark()
                self.click()

            self.performed_events.append(event)
            return True

        except (StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException) as ex:
            print(ex.msg)
            self.excepted_events.append(event)
            return True


    def already_tried(self, event: str) -> bool:
        return event not in self.events or \
               event in self.performed_events or \
               event in self.skipped_events or \
               event in self.excepted_events

    def is_link(self, event: str) -> bool:
        href = self().get_attribute("href")
        if href is not None:
            if not href.endswith("#") and not "javascript:void(0)" in href:# or self.has_link_parent():

                print("Element is a link:", href)
                self.skipped_events.append(event)
                return True
        return False

    def get_element(self) -> WebElement:
        return self.browser.find_element_by_xpath(self.xpath)

    def is_supported(self, event):
        return event == "click"

    def has_link_parent(self):
        try:
            parent = self().find_element_by_xpath("..")
            while parent is not None:
                href = parent.get_attribute("href")
                if href is not None:
                    if not href.endswith("#") and not "javascript:void(0)" in href:
                        return True
                parent = parent.find_element_by_xpath("..")

            return False
        except:
            return True

    def __call__(self, *args, **kwargs) -> WebElement:
        return self.get_element()

    def get_xpath(self) -> str:
        path = self.browser.execute_script(
            "gPt=function(c){if(c.id!==''){return'*[@id=\"'+c.id+'\"]'}if(c===document.body){return c.tagName}var a=0;var e=c.parentNode.childNodes;for(var b=0;b<e.length;b++){var d=e[b];if(d===c){return gPt(c.parentNode)+'/'+c.tagName.toLowerCase()+'['+(a+1)+']'}if(d.nodeType===1&&d.tagName===c.tagName){a++}}};return gPt(arguments[0]);",
            self.element)

        prefix = "//"
        return prefix + path