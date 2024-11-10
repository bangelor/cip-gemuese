from bs4 import BeautifulSoup
from common.data_cleaner import clean_data

class LidlParser:
    def __init__(self, driver, raw_html):
        self.soup = BeautifulSoup(raw_html, 'html.parser')
        self.driver = driver

    def parse_product_details(self):
        """Parse product details from the product page"""
        product_details = {}

        # Extract product name
        name_tag = self.soup.find('span', itemprop='name')
        product_details['name'] = name_tag.text.strip() if name_tag else 'Unknown'

        # Extract price
        price_tag = self.soup.find('strong', {'class': 'pricefield__price', 'itemprop': 'price'})
        product_details['price'] = price_tag['content'] if price_tag and price_tag.has_attr('content') else '0'

        # Extract brand
        brand_tag = self.soup.find('p', class_='brand-name')
        product_details['brand'] = brand_tag.text.strip() if brand_tag else 'NA'

        # Extract origin
        origin_tag = self.soup.find('div', itemprop='description')
        product_details['origin'] = origin_tag.text.strip() if origin_tag else 'NA'

        # Extract weight or unit details
        weight_tag = self.soup.find('span', class_='pricefield__footer')
        product_details['weight'] = weight_tag.text.strip() if weight_tag else 'NA'

        # Extract other attributes as needed...

        return product_details
