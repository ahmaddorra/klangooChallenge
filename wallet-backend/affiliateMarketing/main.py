"""Deal with account creation and saving credentials/account_info"""
import contextlib
from glob import glob
import json
import time, os
import random
import requests
import sys
import pandas as pd
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from affiliateMarketing.objects import Scraper
from mailgun import send_complex_message

CONTAINS_TEXT = "//{tag}[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'{text}')]"

url = "https://www.linkedin.com/search/results/people/?keywords=software%20engineer&origin=SWITCH_SEARCH_VERTICAL&sid=FD8"


class LinkedinScraper(Scraper):
    """
    Account class

    Args:
        Scraper (Parent Class): contains main methods for scraping
    """

    _WAIT_FOR_ELEMENT_TIMEOUT = 30
    __WAIT_FOR_FREE_PHONE_NUMBERS = 10
    _BACKOFF_SECONDS = 10
    driver = None
    list_name = ""
    KOLDMAIL_URL = "https://koldemail.com/dashboard/b2b/features/my-lists"
    data=None
    def __init__(self, url=None):
        """
        Initialize Account Class.


        """
        self.url = url
        self.__account_info = {}

    def login_linkedin(self):
        url = self.url
        self._login(url, "cookies_linkedin")
        # self._save_cookies(os.path.join("cookies", "cookies.pkl"))
        driver = self.driver
        time.sleep(10)
        driver.save_screenshot('/app/img.png')
        el = CONTAINS_TEXT.format(tag="div", text="emails extractor")
        if not self._is_element_available(el):
            driver.refresh()
            time.sleep(10)
            driver.refresh()
            time.sleep(10)
        driver.save_screenshot('/app/img_after_refresh.png')
        self._button_click(el)

        el = "//div[contains(@class,'choices__list--single')]"
        self._button_click(el)

        el = driver.find_element(By.XPATH, "//input[@role='textbox']")
        el.send_keys(self.list_name)
        print(self.list_name, file=sys.stderr)
        time.sleep(1)
        el.send_keys(Keys.RETURN)

        el = CONTAINS_TEXT.format(tag="button", text="extract emails from this search")
        self._button_click(el)
        i=0
        while 1:
            i+=1
            print('checking linkedin results'+ str(i), file=sys.stderr)
            driver.save_screenshot('/app/img_linkedin.png')
            el_end_of_pages = CONTAINS_TEXT.format(
                tag="button", text="no results found"
            )
            el_end_of_pages2 = CONTAINS_TEXT.format(tag="h2", text="no results found")
            el = "//button[@data-stop='Extract emails from this search']"
            for j in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.save_screenshot('/app/img_linkedin_after_scroll.png')
            #lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            #match=False
            #while(match==False):
            #    lastCount = lenOfPage
            #    time.sleep(3)
            #    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            #    if lastCount==lenOfPage:
            #        match=True
             
            #time.sleep(5)
            #try:
            #   driver.find_element(By.XPATH,CONTAINS_TEXT.format(tag="button/span", text='next')+ '/parent::button').is_enabled()
            #except:
            #   breakpoint()
            if (
                not driver.find_elements(By.XPATH, el)
                or driver.find_elements(By.XPATH, el_end_of_pages)
                or driver.find_elements(By.XPATH, el_end_of_pages2)
            ):
                break

            try:
                if (
                    driver.find_elements(
                        By.XPATH,
                        CONTAINS_TEXT.format(tag="button/span", text="next")
                        + "/parent::button",
                    )
                    and not driver.find_element(
                        By.XPATH,
                        CONTAINS_TEXT.format(tag="button/span", text="next")
                        + "/parent::button",
                    ).is_enabled()
                ):
                    break
            except Exception as ex:
                print(ex,file=sys.stderr)
                break
            time.sleep(5)

    def login_intelius(self, url):

        url = "https://intelius.com"
        self._login(url, "cookies_intelius")
        driver = self.driver
        el = "//a[@class='login-button']"
        self._button_click(el)

        el = driver.find_element(By.XPATH, '//input[@type="email"]')
        el.send_keys("")

        el = driver.find_element(By.XPATH, '//input[@type="password"]')

        el.send_keys("")

        el = '//button[@type="submit"]'
        self._button_click(el)

        el = '//button[@type="button"]'
        self._button_click(el)
        time.sleep(10)
        code = get_code()

        el = "//div[@class='code-input-wrapper']/input"
        driver.find_element(By.XPATH, el).send_keys(code)

        el = '//button[@type="submit"]'
        self._button_click(el)

        time.sleep(5)
        self._save_cookies(os.path.join("cookies", "cookies_intelius.pkl"))

    def get_phone_number(name):
        el = "//div[@class='faux-search-input']"
        self._button_click(el)

        el = CONTAINS_TEXT.format(tag="a", text="email")
        self._button_click(el)
        driver.find_element(By.XPATH, "//input[@name='email']").send_keys(
            email
        )

        el = '//button[@type="submit"]'
        self._button_click(el)

        el = CONTAINS_TEXT.format(tag="a", text="open report")
        self._button_click(el)

        el = self._is_element_available(
            "//div[contains(@class,'urls-subsection')]", return_el=True
        )
        els = el.find_elements(By.XPATH, "//a")
        links = [el.text for el in els if any(link in el.text for link in ('facebook', 'instagram', 'twitter') )]

        els = self.driver.find_elements(
            By.XPATH, "//span[contains(@class,'phone-number')]"
        )

        phones = [el.text for el in els]
        
        if verify_phone_number(name):
            return links, phones[0]
        return [], None

    def verify_phone_number(lead_name):
        el = "//div[@class='faux-search-input']"
        self._button_click(el)

        el = CONTAINS_TEXT.format(tag="a", text="phone")
        self._button_click(el)
        driver.find_element(By.XPATH, "//input[@name='phone']").send_keys(
            email
        )

        el = '//button[@type="submit"]'
        self._button_click(el)

        el = CONTAINS_TEXT.format(tag="a", text="open report")
        self._button_click(el)


        els = self.driver.find_elements(
            By.XPATH, "//div[@class='aliases']"
        )
        if any(el.split(' ')[0] in name for el in els):
            return True
        else:
            return False

    def _login(self, url, cookies=None):
        if not self.driver:
            self._get_driver()
        driver = self.driver
        driver.get(url)
        time.sleep(5)
        if cookies:
            self._login_cookies(cookies)
            driver.refresh()
        time.sleep(10)

    def login_kold_email(self):

        if not self.driver:
            url = "https://koldemail.com/login"
            self._login(url)

        driver = self.driver
        el = self._is_element_available('//input[@type="email"]', return_el=True)
        el.send_keys("")

        el = self._is_element_available('//input[@type="password"]', return_el=True)
        el.send_keys("")

        el = '//button[@type="submit"]'
        self._button_click(el)

    def create_list(self):
        driver = self.driver

        driver.get(self.KOLDMAIL_URL)

        el = "//button[@data-target='#newListAccount']"
        self._button_click(el)
        el = self._is_element_available("//input[@name='listName']", return_el=True)
        #self.list_name = f"test-{int(time.time())}"
        print(self.list_name,file=sys.stderr)
        el.send_keys(self.list_name)

        el = CONTAINS_TEXT.format(tag="button", text="create this list")
        self._button_click(el)

    def get_list(self):
        driver = self.driver
        driver.get(self.KOLDMAIL_URL)

        el = f"//tr/td/input[@value='{self.list_name}']/parent::td/parent::tr/td/span/{CONTAINS_TEXT.format(tag='a', text='view the data')[2:]}"

        self._button_click(el)

        el = CONTAINS_TEXT.format(tag="span", text="copy view to clipboard")
        self._button_click(el)
        return pd.read_clipboard()

    # def create_kold_email_list(self, lst):
    #     driver = self.driver
    #     driver.get("https://koldemail.com/dashboard/b2b/features/my-lists")

    def get_leads(self):
        self.login_kold_email()

        return self.get_list()

    def get_scraped_data(self, url, email,list_name, id):
        # url="https://www.linkedin.com/search/results/people/?keywords=software%20engineer&origin=SWITCH_SEARCH_VERTICAL&sid=GgL"
        print(list_name)
        account = LinkedinScraper(url=url)
        account.list_name= list_name
        account.login_kold_email()
        print("kold email logged in", file=sys.stderr)
        logging.info("kold email logged in")
        time.sleep(10)
        account.create_list()

        print('list created' , file=sys.stderr)
        account.login_linkedin()
        print('linkedin logged in', file=sys.stderr)
        logging.info("Linkedin logged in")
        df = account.get_list()
        df.to_csv(f"{os.path.join('/app','scraped_data',list_name)}.csv")
        print('list saved', file=sys.stderr)
        logging.info("list saved")
        send_complex_message(list_name, email)
        print('email sent', file=sys.stderr)
        logging.info("email sent")
        account.driver.quit()
        self.data= df


if __name__ == "__main__":
    account = LinkedinScraper(
        url="https://www.linkedin.com/search/results/people/?keywords=software%20engineer&origin=SWITCH_SEARCH_VERTICAL&sid=GgL"
    )
    account.login_kold_email()
    time.sleep(10)
    account.create_list()
    account.login_linkedin()
    email = 'msri.ahmad@gmail.com'
    df = account.get_list()
    send_complex_message(account.list_name, email)

    account.login_intelius()
