# stores/migros/migros_parser.py
from bs4 import BeautifulSoup
from common.data_cleaner import clean_data

class MigrosParser:
    def __init__(self, raw_html):
        self.soup = BeautifulSoup(raw_html, 'html.parser')

    def parse(self):
        """Extract product names and prices from the Migros HTML page"""
        products = []
        for product in self.soup.select('.product'):
            name = product.select_one('.product-name').text
            price = product.select_one('.product-price').text
            products.append({
                'name': clean_data(name),
                'price': clean_data(price)
            })
        return products
