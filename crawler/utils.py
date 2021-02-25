from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver import FirefoxProfile
from seleniumrequests import PhantomJS, Firefox
from urllib.parse import urlparse
from url_normalize import url_normalize
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib.parse import urldefrag
from selenium.webdriver.support.ui import WebDriverWait
from tld import get_tld

def get_firefox():
    caps = DesiredCapabilities().FIREFOX
    options = FirefoxOptions()
    #options.add_argument("--headless")
    caps["pageLoadStrategy"] = "eager"  # interactive
    profile = FirefoxProfile()
    profile.set_preference("dom.disable_beforeunload", True)
    browser = Firefox(desired_capabilities=caps,firefox_profile=profile, options=options, executable_path="A:/WebDrivers/geckodriver.exe")
    browser.set_page_load_timeout(6)
    return browser

def get_browser():
    return get_firefox()