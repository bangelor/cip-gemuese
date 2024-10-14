# stores/migros/migros_parser.py
from bs4 import BeautifulSoup
from common.data_cleaner import clean_data

class MigrosParser:
    def __init__(self, raw_html):
        self.soup = BeautifulSoup(raw_html, 'html.parser')

    def parse(self):
        """Extract product names and prices from the Migros vegetable section"""
        products = []

        # Find all product cards in the HTML
        for product in self.soup.find_all('article', class_='product-card'):
            # Extract the product name
            name_tag = product.find('span', {'data-cy': lambda x: x and 'product-name' in x})
            # Extract the product price
            price_tag = product.find('span', {'data-cy': lambda x: x and 'current-price' in x})

            if name_tag and price_tag:
                name = clean_data(name_tag.text)
                price = clean_data(price_tag.text)
                
                products.append({
                    'name': name,
                    'price': price
                })

        return products
