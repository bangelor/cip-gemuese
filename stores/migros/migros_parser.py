# stores/migros/migros_parser.py
from bs4 import BeautifulSoup
from common.data_cleaner import clean_data
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class MigrosParser:
    def __init__(self, driver, raw_html):
        """
        Initialize the parser with the raw HTML from the product listing page and a Selenium WebDriver.
        """
        self.soup = BeautifulSoup(raw_html, 'html.parser')
        self.driver = driver  # Selenium WebDriver to interact with the site

    def parse(self):
        """Extract product names and prices from the Migros vegetable section"""
        products = []

        # Find all product cards in the HTML
        for product in self.soup.find_all('article', class_='product-card'):
            # Extract the product name
            name_tag = product.find('span', {'data-cy': lambda x: x and 'product-name' in x})
            # Extract the product price
            price_tag = product.find('span', {'data-cy': lambda x: x and 'current-price' in x})
            # Extract the product detail page URL (assuming it's in the href attribute)
            product_link_tag = product.find('a', class_='show-product-details')

            if name_tag and price_tag and product_link_tag:
                name = clean_data(name_tag.text)
                price = clean_data(price_tag.text)
                product_url = product_link_tag['href']

                # Navigate to the product detail page to scrape more information
                product_details = self._extract_product_details(product_url)
                
                # Combine the data into the product dictionary
                products.append({
                    'name': name,
                    'price': price,
                    **product_details  # Add the additional details from the product page
                })

        return products

    def _extract_product_details(self, product_url):
        """
        Navigate to the product detail page and extract additional details like weight and description.
        """
        product_details = {}
        
        # Navigate to the product detail page using Selenium
        full_url = f"https://www.migros.ch{product_url}"  # Ensure the URL is absolute
        self.driver.get(full_url)

        # Wait for the page to load (you can replace with explicit waits if necessary)
        time.sleep(3)  # This may vary depending on your internet speed and page load time

        # Extract the new page's HTML after navigation
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Extract additional product details (modify these based on actual tags/classes on the product detail page)
        description_tag = soup.find('span', {'data-cy': 'product-description'})
        weight_tag = soup.find('span', {'data-cy': 'product-weight'})
        
        if description_tag:
            product_details['description'] = clean_data(description_tag.text)
        
        if weight_tag:
            product_details['weight'] = clean_data(weight_tag.text)

        # You can add more fields as necessary (e.g., ingredients, product labels, etc.)

        return product_details
