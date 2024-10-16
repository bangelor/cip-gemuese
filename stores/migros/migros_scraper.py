# stores/migros/migros_scraper.py
from common.selenium_utils import SeleniumDriver
from config.migros_config import MIGROS_URL
from stores.migros.migros_parser import MigrosParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException 

import time

class MigrosScraper:
    def __init__(self):
        self.driver = SeleniumDriver()

    def scrape(self):
        """Method to start scraping Migros vegetable section"""
        self.driver.get(MIGROS_URL)
        # Wait for the product grid to load
        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-card')))
            raw_html = self.driver.get_page_source()
            return raw_html
        except:
            print(f"Website not found, aborting...")
            return ''
             

    def scrape_and_parse(self):
        """Scrape and then parse the result"""
        raw_html = self.scrape()
        parser = MigrosParser(self.driver, raw_html)
        parsed_data = parser.parse()

        # Navigate to each product's detail page and extract additional info
        self._scrape_product_details(parsed_data)

        return parsed_data

    def _scrape_product_details(self, products):
        """Click on each product to navigate to the product detail page and extract more information."""
        for product in products:
            product_url = product.get('product_url')
            if product_url:
                full_url = f"https://www.migros.ch{product_url}"
                print(f"Scraping details for product: {product.get('name')} at {full_url}")
                self.driver.get(full_url)

                try:
                    # Wait for a specific element on the product detail page to load (increase timeout to 30 seconds)
                    WebDriverWait(self.driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-detail')))

                    # Get the page source for parsing
                    product_detail_html = self.driver.get_page_source()

                    # Initialize a new parser for product details
                    parser = MigrosParser(self.driver, product_detail_html)

                    # Parse the product details
                    product_details = parser._parse_product_details(product_detail_html)

                    # Add the additional details to the product dictionary
                    product.update(product_details)

                except TimeoutException:
                    print(f"Product details not found for {product.get('name')}, skipping...")

            else:
                print(f"Skipping product: {product.get('name')} as it has no valid URL.")


    def close(self):
        """Close the Selenium driver"""
        self.driver.quit()
