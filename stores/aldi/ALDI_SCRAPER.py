# stores/aldi/aldi_scraper.py
from config.aldi_config import ALDI_URL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from common.data_cleaner import clean_data, chatGPT_simplify_names, price_per_unit
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
from datetime import datetime


class AldiScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def get_all_pages(self, url):
        """Get all pagination links from the category page."""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pagination__item')))
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            pagination_links = soup.select("li.pagination__item a")
            all_pages = [ALDI_URL + link.get("href") for link in pagination_links]
            return all_pages
        except Exception as e:
            print(f"Error fetching pagination: {e}")
            return []
        finally:
            self.driver.quit()

    def get_product_links(self, soup):
        """Extract all product links from a page's soup."""
        try:
            links = soup.select("div.product-item__info a")
            product_links = [ALDI_URL + link.get("href") for link in links]
            return product_links
        except Exception as e:
            print(f"Error extracting product links: {e}")
            return []

    def extract_data(self, url):
        """Extract detailed data from a single product page."""
        try:
            page = requests.get(url, timeout=10)
            soup = BeautifulSoup(page.text, 'html.parser')

            product_name = chatGPT_simplify_names(soup.select_one("section.product-configurator h1").text.strip())
            product_price = float(clean_data(soup.select_one("span.volume-price__amount span").text.strip()))
            product_amount = clean_data(soup.find("div", class_="text-secondary spacing-right").text.strip())
            converted_to_price_per_kg_or_pc = price_per_unit(product_price, product_amount)
            product_price_per_amount = converted_to_price_per_kg_or_pc[0]
            unit = converted_to_price_per_kg_or_pc[1]

            country_origin_test = soup.select("div.tags-and-product-description div")[1].text.strip()
            country_origin = country_origin_test if "Ursprungsland" in country_origin_test else "NA"

            elements = soup.select("div.grid.ingredients-and-allergens")
            additional_info = " ".join([element.text.strip() for element in elements])

            return {
                "name": product_name,
                "price": product_price,
                "amount": product_amount,
                "price_per_amount": product_price_per_amount,
                "unit": unit,
                "price_unit": converted_to_price_per_kg_or_pc,
                #"origin": country_origin,
                'store': 'aldi',
                #"characteristics": additional_info,
            }
        except Exception as e:
            print(f"Error extracting data from {url}: {e}")
            return None

    def fetch_all_product_links(self, pages):
        """Collect all product links from multiple pages."""
        all_links_products = []
        for page_url in pages:
            try:
                page = requests.get(page_url, timeout=10)
                soup = BeautifulSoup(page.text, 'html.parser')
                product_links = self.get_product_links(soup)
                all_links_products.extend(product_links)
                time.sleep(1)  # Pause to avoid server overload
            except requests.RequestException as e:
                print(f"Error fetching product links from {page_url}: {e}")
        return all_links_products

    def scrape(self, url):
        """Main scraping logic for collecting product data."""
        start_time = time.time()

        # Step 1: Get all pagination pages
        print("Fetching pagination links...")
        all_pages = self.get_all_pages(url)

        if not all_pages:
            print("No pagination links found. Exiting.")
            return None

        # Step 2: Fetch all product links across all pages
        print("Fetching product links from all pages...")
        all_product_links = self.fetch_all_product_links(all_pages)

        if not all_product_links:
            print("No product links found. Exiting.")
            return None

        # Step 3: Extract data from each product link
        print("Extracting data from product pages...")
        data = [self.extract_data(link) for link in all_product_links if link]
        data = [d for d in data if d is not None]  # Filter out None results

        if not data:
            print("No data extracted. Exiting.")
            return None

        # Step 4: Convert the data into a DataFrame
        df = pd.DataFrame(data)

        # Calculate and print execution time
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.2f} seconds")

        # Save the DataFrame to an Excel file
        # now = datetime.now()
        # file_name = f"aldi_obst_gemuse_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
        # df.to_excel(file_name, index=False)
        # print(f"Data has been saved to {file_name}")

        return df

    def close(self):
        """Close the Selenium driver."""
        self.driver.quit()
