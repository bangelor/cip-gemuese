# common/selenium_utils.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class SeleniumDriver:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def get(self, url):
        self.driver.get(url)

    def get_page_source(self):
        return self.driver.page_source

    def quit(self):
        self.driver.quit()
