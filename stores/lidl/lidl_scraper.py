from common.selenium_utils import SeleniumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from stores.lidl.lidl_parser import LidlParser
import time

class LidlScraper:
    def __init__(self):
        self.driver = SeleniumDriver()

    def scrape_category_urls(self, base_url):
        """Scrape category URLs from the Lidl website"""
        self.driver.get(base_url)
        try:
            category_element = self.driver.find_element(By.XPATH, "//a[@aria-label='Obst & Gemüse']")
            parent_li = category_element.find_element(By.XPATH, "..")
            ul_element = parent_li.find_element(By.TAG_NAME, "ul")
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")

            category_urls = []
            for li in li_elements:
                try:
                    link = li.find_element(By.TAG_NAME, "a")
                    category_urls.append(link.get_attribute("href"))
                except NoSuchElementException:
                    continue

            return category_urls

        except NoSuchElementException:
            print("Category elements not found.")
            return []
        finally:
            self.driver.quit()

    def scrape_product_urls(self, category_urls):
        """Scrape product URLs from each category"""
        product_urls = []
        for url in category_urls:
            self.driver.get(url)
            time.sleep(1)  # Allow time for page loading

            while True:
                product_elements = self.driver.find_elements(By.CLASS_NAME, "product-item-link")
                for product in product_elements:
                    product_urls.append(product.get_attribute("href"))

                try:
                    load_more_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "amscroll-load-button-new"))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                    time.sleep(1)
                    load_more_button.click()
                    time.sleep(2)
                except (TimeoutException, StaleElementReferenceException):
                    break

        self.driver.quit()
        return product_urls

    def scrape_and_parse(self, product_urls):
        """Scrape and parse product details from product pages"""
        products = []
        for url in product_urls:
            self.driver.get(url)
            time.sleep(1)  # Allow time for page loading
            raw_html = self.driver.get_page_source()
            parser = LidlParser(self.driver, raw_html)
            product_data = parser.parse_product_details()
            products.append(product_data)

        self.driver.quit()
        return products

    def close(self):
        """Close the Selenium driver"""
        self.driver.quit()
