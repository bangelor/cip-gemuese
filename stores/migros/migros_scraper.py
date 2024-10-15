# stores/migros/migros_scraper.py
from common.selenium_utils import SeleniumDriver
from config.migros_config import MIGROS_URL
from stores.migros.migros_parser import MigrosParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
        # Scrape the initial product listing page
        raw_html = self.scrape()
        
        # Initialize the parser with the raw HTML
        parser = MigrosParser(self.driver, raw_html)  # Pass the driver for product page navigation
        
        # Parse and extract product details
        parsed_data = parser.parse()

        # Navigate to each product's detail page and extract additional info
        self._scrape_product_details(parsed_data)

        return parsed_data

    def _scrape_product_details(self, products):
        """
        Click on each product to navigate to the product detail page 
        and extract additional information.
        """
        for product in products:
            product_url = product.get('product_url')
            if product_url:
                full_url = f"https://www.migros.ch{product_url}"  # Ensure URL is absolute
                self.driver.get(full_url)

                # Wait for the product detail page to load (adjust selectors as needed)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-detail')))

                # Get the page source for parsing
                product_detail_html = self.driver.get_page_source()
                
                # Use a separate parser or method to extract more information
                product_details = self._parse_product_details(product_detail_html)
                
                # Add the additional details to the product dictionary
                product.update(product_details)

    def _parse_product_details(self, raw_html):
        """
        Parse additional product details from the product detail page.
        """
        parser = BeautifulSoup(raw_html, 'html.parser')
        product_details = {}

        # Extract relevant details (adjust these based on the actual HTML structure)
        description_tag = parser.find('span', {'data-cy': 'product-description'})
        weight_tag = parser.find('span', {'data-cy': 'product-weight'})
        
        if description_tag:
            product_details['description'] = description_tag.text.strip()
        
        if weight_tag:
            product_details['weight'] = weight_tag.text.strip()

        # Add more fields as necessary
        
        return product_details

    def close(self):
        """Close the Selenium driver"""
        self.driver.quit()
