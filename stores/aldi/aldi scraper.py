from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from itertools import chain
from datetime import datetime
import csv



# Base URL for Aldi product pages
BASE_URL = "https://www.aldi-now.ch/de/obst-&-gem%C3%BCse"


def navigate_aldi_webpage(BASE_URL):
    """
    This section of the code extracts all links from the subcategory fruit and vegetable
    in a first step navigate to the aldi website and click on the togglers which shows then
    all links of the subcategories
    """
    driver = webdriver.Chrome()
    driver.get(BASE_URL)

    time.sleep(3)

    button_accept = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    button_accept.click()

    time.sleep(3)

    #find the subset of the links
    subset_obst_html = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/main/form/div[1]/section/div[3]/div[2]/div/div/ul/li[9]/div/div[2]/div/ul")

    extenders = subset_obst_html.find_elements(By.CSS_SELECTOR, ".toggler-item__arrow--filter.js-catalog__toggler-trigger")

    print(extenders)

    #click on all the togglers so that every link in the obst&gemüse section can be seen
    for extender in extenders:
        extender.click()
        time.sleep(3)

    #now get the updated html and look for all the links

    updated_html_subset = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/main/form/div[1]/section/div[3]/div[2]/div/div/ul/li[9]/div")


    #get all the links from subcategory

    links_level_3 = updated_html_subset.find_elements(By.CSS_SELECTOR, "li.filter-category__item--level-3 button.filter-category__link.js-catalog__trigger")

    level_3_urls = [link.get_attribute("data-url") for link in links_level_3]


    #get all the links from subset

    all_links = updated_html_subset.find_elements(By.CSS_SELECTOR, "li.filter-category__item--level-2 button.filter-category__link.js-catalog__trigger" )

    all_urls = [link.get_attribute("data-url") for link in all_links]


    #delete the links which are redundant

    links_redundant = list(set([os.path.dirname(x) for x in level_3_urls]))

    #links_products

    links_products = [("https://www.aldi-now.ch" + x ) for x in all_urls if x not in links_redundant]

    return links_products
    driver.quit()





url = navigate_aldi_webpage(BASE_URL)
BASE_ALDI = "https://www.aldi-now.ch"
print(url)


def get_product_links(url, category):
    """get all the product links on the page"""
    try:
        # Select product links from the page
        page = requests.get(url, timeout = 10)
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.select("div.product-item__info a")
        websites = [(BASE_ALDI + link.get("href"), category) for link in links]
        return websites
    except Exception as e:
        print(f"Error extracting product links: {e}")
        return []


def get_category(url):
    category = "/".join(url.rsplit("/", 2)[-2:])
    return category

#create a list with the category
category_lst = [get_category(x) for x in url]
#create a tupel with the category
tupel_url = list(zip(url,category_lst))

#get all the links from the websites
product_links = [get_product_links(url, category) for url,category in tupel_url]

#entschachtelung der liste in der list
product_links = list(chain(*product_links))
print(product_links)



def extract_data(url, category):
    """extract all the data from the product such as name, price, amount
    pricer per amount, if available country of origin and additional data"""
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.text, 'html.parser')

        # Extract product details
        product_name = soup.select_one("section.product-configurator h1").text.strip()
        product_price = soup.select_one("span.volume-price__amount span").text.strip()
        product_amount = soup.find("div", class_="text-secondary spacing-right").text.strip()
        product_price_per_amount = soup.find_all("div", class_="text-secondary")[1].text.strip()

        # Extract country of origin
        country_origin_test = soup.select("div.tags-and-product-description div")[1].text.strip()
        country_origin = country_origin_test if "Ursprungsland" in country_origin_test else "NA"

        # Extract additional information (ingredients, allergens)
        elements = soup.select("div.grid.ingredients-and-allergens")
        additional_info = " ".join([element.text.strip() for element in elements])

        #add time
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "name": product_name,
            "price": product_price,
            "amount": product_amount,
            "price_per_amount": product_price_per_amount,
            "country_origin": country_origin,
            "additional_info": additional_info,
            "category": category,
            "time": date_time
        }
    except Exception as e:
        print(f"Error extracting data from {url}: {e}")
        return None


data = [extract_data(link, category) for link,category in product_links if link]
data = [d for d in data if d is not None]  # Filter out any None results due to errors

    # Convert the data into a DataFrame
df = pd.DataFrame(data)


print(df)

now = datetime.now()
date_time = now.strftime("%Y%m%d %H_%M_%S")

filename_csv = f"aldi_{date_time}.csv"
filename_excel = f"aldi_{date_time}.xlsx"
directory = "C:\\Users\\41798\\Desktop\\CIP\\cip-gemuese\\storage\\"
full_path_csv = os.path.join(directory,filename_csv)
full_path_excel = os.path.join(directory,filename_excel)

df.to_csv(full_path_csv, index=False)

df.to_excel(full_path_excel, index=False)















