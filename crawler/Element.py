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
        if not self.check_event(event) and self.check_link_event(event):
            return
        try:
            if event == "click":
                self.mark()
                self.click()

            self.performed_events.append(event)

        except (StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException) as ex:
            print(ex.msg)
            self.excepted_events.append(event)


    def check_event(self, event: str) -> bool:
        return event in self.events and \
               event not in self.performed_events and \
               event not in self.skipped_events and \
               event not in self.excepted_events

    def check_link_event(self, event: str) -> bool:
        href = self().get_attribute("href")
        if href is not None and not "javascript:void(0)" in href:
            print("Element is a link:", href)
            self.skipped_events.append(event)
            return False
        return True

    def get_element(self) -> WebElement:
        return self.browser.find_element_by_xpath(self.xpath)

    def __call__(self, *args, **kwargs) -> WebElement:
        return self.get_element()

    def get_xpath(self) -> str:
        return self.browser.execute_script(
            "gPt=function(c){if(c.id!==''){return'id(\"'+c.id+'\")'}if(c===document.body){return c.tagName}var a=0;var e=c.parentNode.childNodes;for(var b=0;b<e.length;b++){var d=e[b];if(d===c){return gPt(c.parentNode)+'/'+c.tagName.toLowerCase()+'['+(a+1)+']'}if(d.nodeType===1&&d.tagName===c.tagName){a++}}};return gPt(arguments[0]);",
            self.element)