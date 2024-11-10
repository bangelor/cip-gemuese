from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

# Base URL for Aldi product pages
BASE_URL = "https://www.aldi-now.ch"

# Function to get all pagination links
def get_all_pages(url):
    """get all the page links on the bottom from 1 to 4"""
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.text, 'html.parser')
        pagination_links = soup.select("li.pagination__item a")
        all_pages = [BASE_URL + x.get("href") for x in pagination_links]
        return all_pages
    except requests.RequestException as e:
        print(f"Error fetching pagination: {e}")
        return []

# Function to extract product links from a page
def get_product_links(soup):
    """get all the product links on the page"""
    try:
        # Select product links from the page
        links = soup.select("div.product-item__info a")
        websites = [BASE_URL + link.get("href") for link in links]
        return websites
    except Exception as e:
        print(f"Error extracting product links: {e}")
        return []

# Function to extract product data from a single product page
def extract_data(url):
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

        return {
            "name": product_name,
            "price": product_price,
            "amount": product_amount,
            "price_per_amount": product_price_per_amount,
            "country_origin": country_origin,
            "additional_info": additional_info,
        }
    except Exception as e:
        print(f"Error extracting data from {url}: {e}")
        return None

# Function to get all product links across multiple pages
def fetch_all_product_links(pages):
    """gather all productlinks from all four pages in one list"""
    all_links_products = []
    for page_url in pages:
        try:
            page = requests.get(page_url, timeout=10)
            soup = BeautifulSoup(page.text, 'html.parser')
            product_links = get_product_links(soup)
            all_links_products.extend(product_links)
            time.sleep(1)  # Short pause to avoid overloading the server
        except requests.RequestException as e:
            print(f"Error fetching product links from {page_url}: {e}")
    return all_links_products

# Main function to gather data and store it in a DataFrame
def scrape_aldi_products(url):
    """
    1.step get all the four links with products in the section obst & gemuese
    2.step get all the productlinks from all four pages
    3.step parse the data from the links
    4.step save the information in a dataframe
    """
    start_time = time.time()

    # Fetch all pagination pages
    all_pages = get_all_pages(url)

    # Fetch all product links across all pages
    all_links_products = fetch_all_product_links(all_pages)

    # Extract data for each product link
    data = [extract_data(link) for link in all_links_products if link]
    data = [d for d in data if d is not None]  # Filter out any None results due to errors

    # Convert the data into a DataFrame
    df = pd.DataFrame(data)

    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")

    return df

# URL for the Aldi product category (Obst & Gemüse)
aldi_url = "https://www.aldi-now.ch/de/obst-&-gem%C3%BCse?ipp=36"

# Scrape the products and create a DataFrame
df = scrape_aldi_products(aldi_url)

# Save the DataFrame to an Excel file
df.to_excel("aldi_obst_gemuse_preise_verbessert.xlsx", index=False)
print("Data has been saved to aldi_obst_gemuse_preise.xlsx")
