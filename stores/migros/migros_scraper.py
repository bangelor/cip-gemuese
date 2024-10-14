# stores/migros/migros_scraper.py
from common.selenium_utils import SeleniumDriver
from config.migros_config import MIGROS_URL
from stores.migros.migros_parser import MigrosParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MigrosScraper:
    def __init__(self):
        self.driver = SeleniumDriver()

    def scrape(self):
        """Method to start scraping Migros vegetable section"""
        self.driver.get(MIGROS_URL)
        # Wait for the product grid to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-card')))
        raw_html = self.driver.get_page_source()
        return raw_html

    def scrape_and_parse(self):
        """Scrape and then parse the result"""
        raw_html = self.scrape()
        parser = MigrosParser(raw_html)
        parsed_data = parser.parse()
        return parsed_data

    def close(self):
        self.driver.quit()
