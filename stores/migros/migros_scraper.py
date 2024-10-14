# stores/migros/migros_scraper.py
from common.selenium_utils import SeleniumDriver
from config.migros_config import MIGROS_URL
from stores.migros.migros_parser import MigrosParser

class MigrosScraper:
    def __init__(self):
        self.driver = SeleniumDriver()

    def scrape(self):
        """Method to start scraping Migros website"""
        self.driver.get(MIGROS_URL)
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

# Example usage:
# from stores.migros.migros_scraper import MigrosScraper
# scraper = MigrosScraper()
# data = scraper.scrape_and_parse()
# scraper.close()
