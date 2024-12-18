# stores/migros/migros_parser.py
from bs4 import BeautifulSoup
from common.data_cleaner import clean_data

class MigrosParser:
    def __init__(self, driver, raw_html):
        self.soup = BeautifulSoup(raw_html, 'html.parser')
        self.driver = driver  # Selenium WebDriver to interact with the site

    def parse(self):
        """Extract product names and prices from the Migros vegetable section"""
        products = []
        
        for product in self.soup.find_all('article', class_='product-card'):
            print(f'scraping Product: {product}')
            # Extract the product name
            name_tag = product.find('span', {'data-cy': lambda x: x and 'product-name' in x})
            if name_tag:
                name = clean_data(name_tag.text)
            else:
                name = 'Unknown'

            # Extract the product price
            price_tag = product.find('span', {'data-cy': lambda x: x and 'current-price' in x})
            if price_tag:
                price = clean_data(price_tag.text)
            else:
                price = 'NA'

            # Extract 'Gewicht'
            amount_tag = product.find('span', {'class': lambda x: x and 'weight-priceUnit' in x})
            if amount_tag:
                amount = clean_data(amount_tag.text)
            else:
                amount = 'NA'

            # Extract the product URL
            url_tag = product.find('a', href=True)
            if url_tag:
                product_url = url_tag['href']
            else:
                product_url = None

            products.append({
                'name': name,
                'price': price,
                'amount': amount,
                'product_url': product_url  # Include product URL for detail scraping
            })

        return products


    def _parse_product_details(self, raw_html):
        """Parse additional product details from the product detail page."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        product_details = {}

        # # Extract 'Marke & Labels'
        # brand_label_tag = soup.find('dd', {'data-cy': lambda x: x and 'marke_&_labels' in x})
        # if brand_label_tag:
        #     product_details['brand_labels'] = clean_data(brand_label_tag.text)

        # Extract 'Eigenschaften'
        characteristics_tag = soup.find('dd', {'data-cy': lambda x: x and 'eigenschaften' in x})
        if characteristics_tag:
            product_details['characteristics'] = clean_data(characteristics_tag.text)
        else: 
            product_details['characteristics'] = 'NA'
        # Extract 'Produktionsland'
        origin_tag = soup.find('dd', {'data-cy': lambda x: x and 'origin' in x})
        if origin_tag:
            product_details['origin'] = clean_data(origin_tag.text)
        else:
            product_details['origin'] = 'NA'
        # # Extract 'Bewertung' (Rating)
        # rating_tag = soup.find('dd', {'data-cy': lambda x: x and 'rating' in x})
        # if rating_tag:
        #     rating_value_tag = rating_tag.find('rect', {'fill': '#333'})
        #     if rating_value_tag:
        #         rating_width = rating_value_tag.get('width', 0)
        #         product_details['rating'] = f"{float(rating_width)/20:.1f}/5"  # Assuming 20px = 1 star

        return product_details
