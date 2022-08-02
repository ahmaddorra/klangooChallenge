from dataclasses import dataclass
from glob import glob
import os
import pickle
import sys
from time import sleep
import random
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import os
#from pyvirtualdisplay import Display
#os.environ["DISPLAY"] = ":1"
#display = Display(visible=0, size=(1920,1080))
#display.start()

os.environ["DISPLAY"] = ":1"

PROXY_HOST = ""
PROXY_PORT = ""
PROXY_USER = ""
PROXY_PASS = ""


class CookiesNotFound(Exception):
    """Raised when the cookies file is not found."""

    pass


@dataclass
class Scraper:
    """
    Base Class for the scraper.

    Contain:
        - _login_cookies (load cookies into the browser)
        - _button_click (Clicks the button after waiting for it to be clickable)
        - _add_proxy (Adds proxy to the selenium driver)
        - is_signed_in (Checks if the current page is logged in)
        - _find_first_available_element (?)

    """

    driver: Chrome = None
    _WAIT_FOR_ELEMENT_TIMEOUT: int = 20

    def _get_driver(self):
        if self.driver is not None:
            self.driver.quit()
        # chrome_options = self._add_proxy()
        chrome_options = uc.ChromeOptions()
        # chrome_options.add_argument("--no-sandbox --no-first-run --no-service-autorun --password-store=basic")

        # chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # chrome_options.add_experimental_option(
        #     "prefs",
        #     {
        #         "extensions.ui.developer_mode": True,
        #     },
        # )
        # chrome_options.add_argument(
        #     "--user-data-dir=C:\\devprojects\\linkedin-sales-navigator\\data\\Profile3"
        # )

        chrome_options.add_argument(
            f"--load-extension=./extension_koldemail-com"
        )
        #chrome_options.add_argument('headless')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        #uc.TARGET_VERSION=101
        chrome_options.add_experimental_option('w3c', True)
        self.driver = uc.Chrome(chrome_options=chrome_options)

    def _save_cookies(self, path):
        """Save cookies to be used later"""
        driver = self.driver
        try:
            with open(path, "wb") as file_handler:
                pickle.dump(driver.get_cookies(), file_handler)
        except Exception as ex:
            # This is useful to pass on a better error message
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, f"Exception: {ex}")

    def _login_cookies(self, email=None):
        """
        Login to Linkedin using cookies

        Args:
            email (string, optional): If email is not specified, a cookies file is chosen by random. Defaults to None.
        """

        if email:
            file = os.path.join("cookies", f"{email}.pkl")
            error_msg = "cookies file doesn't exist"
        else:
            file = random.choice(glob("cookies" + "/*.pkl"))
            error_msg = "Cookies folder is empty"
        if not os.path.isfile(file):
            raise CookiesNotFound(error_msg)
        try:
            with open(file, "rb") as cookiesfile:
                cookies = pickle.load(cookiesfile)
                print("cookies", cookies, len(cookies))
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as ex:
                        print("Exception while looping through cookies:", ex)
        except Exception as ex:
            print(f"Exception loading cookies from pkl file {file} :", ex)

    # @check_captcha
    def _button_click(self, xpath, inside_iframe=False):
        """
        Clicks a button.

        It waits for the element to be clickable. Afterwards,
        wait x seconds and click the element.

        Args:
            xpath (_type_): _description_
            inside_iframe (bool, optional): _description_. Defaults to False.
        """
        self.prev_button = xpath
        if inside_iframe:
            _xpath = '//iframe[contains(@title,"Security verification")]'
            iframe = WebDriverWait(self.driver, self._WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, _xpath))
            )
            self.driver.switch_to.frame(iframe)

        button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    xpath,
                )
            )
        )
        sleep(2)
        button.click()

        self.driver.switch_to.default_content()

    def _is_element_available(self, xpath, return_el=False):
        """
        Check is element available without exceptions

        Args:
            xpath (string): xpath of the element
            return_el (bool, optional):  Defaults to False.

        Returns:
            book or element: return if element available or return element if found.
        """
        try:
            el = WebDriverWait(self.driver, self._WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if return_el:
                return el
            return True
        except Exception as ex:
            return False

    def _add_proxy(self):
        """
        Add a proxy via an extension to chrome driver

        Return: Chrome options object
        """

        chrome_options = uc.ChromeOptions()
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (
            PROXY_HOST,
            PROXY_PORT,
            PROXY_USER,
            PROXY_PASS,
        )
        plugin_file = "proxy_auth_plugin.zip"

        with zipfile.ZipFile(plugin_file, "w") as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(plugin_file)
        return chrome_options

    def is_signed_in(self):
        """
        Check if the page is signed_in.

        Searches for an element, only available in signed pages

        Returns:
            Binary: True if the page is signed otherwise False
        """
        try:
            WebDriverWait(self.driver, self._WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, c.VERIFY_LOGIN_ID))
            )
            return True
        except:  # if this element is not present, then the page isn't logged in
            pass
        return False

    @classmethod
    def _find_first_available_element(cls, *args):
        for elem in args:
            if elem:
                return elem[0]
