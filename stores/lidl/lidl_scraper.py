# Load Packages
# Scraping
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Parsing
from bs4 import BeautifulSoup

# Technical & Operations
import pandas as pd
from datetime import datetime
import os
import time
##################################################################################

# The goal is to apply a top-down approach, starting from the main category (level 0) and working down to individual food items (Level 2).
# 1) Retrieve essential information for Level 1 (subcategory): This includes the subcategory name and the corresponding URL.
# Start the WebDriver
driver = webdriver.Chrome()

# Navigate to the target website
driver.get("https://sortiment.lidl.ch/de/obst-gemuse#/")  # Adjust the website URL as necessary

# Locate the <a> element with aria-label "Obst & Gemüse"
a_element = driver.find_element(By.XPATH, "//a[@aria-label='Obst & Gemüse']")

# Navigate to the parent <li> element
li_element = a_element.find_element(By.XPATH, "..")  # ".." moves to the parent element

# Find the <ul> element containing the children elements
ul_children = li_element.find_element(By.TAG_NAME, "ul")

# Locate all child items (<li> elements) within the <ul>
children_items = ul_children.find_elements(By.TAG_NAME, "li")

# Output child items and their URLs
url_subcategories = []
title_subcategories = []

for child in children_items:
    try:
        # Find the <a> tag within the <li> element
        link = child.find_element(By.TAG_NAME, "a")
        url_subcategories.append(link.get_attribute("href"))
        title_subcategories.append(link.get_attribute("title"))
    except Exception as e:
        break

# Close the WebDriver
driver.quit()

##################################################################################
# 2) Find URLs of all food items for each subcategory (Level 2).
# URLs for each subcategory are dynamically retrieved, clicking a button for pages with more than 18 items.

urls = []
subcat = []
e = 0
z = 0

for i in url_subcategories:
    
    # Set up Selenium WebDriver (with automatic ChromeDriver download)
    driver = webdriver.Chrome()
    
    # List to store URLs
    # Start URL
    current_url = url_subcategories[e]
    current_subcat = title_subcategories[e]
    
    e += 1
    
    while True:
        driver.get(current_url)  # Navigate to the current URL
        time.sleep(1)  # Wait to ensure the page is loaded
        urls.append(driver.current_url)
        subcat.append(current_subcat)
        
        # Banner-Button find and click on
        try:
            accept_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            accept_button.click()
        except Exception as e:
            break

        # Loop for scrolling and clicking the button
        while True:
            try:
                # Wait until the button appears (max. 10 seconds)
                wait = WebDriverWait(driver, 10)
                bs = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "amscroll-load-button-new")))
                
                if bs.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", bs)
                    time.sleep(1)  # Wait to ensure the page loads after scrolling
                    driver.execute_script("arguments[0].click();", bs)
                    time.sleep(2)  # Wait after the click
                    current_url = driver.current_url  # Update the current URL
                    urls.append(current_url)  # Save the new URL
                    subcat.append(current_subcat)
                else:
                    break  # Exit the inner loop if the button is no longer available
            except TimeoutException:
                break  # Exit the loop if the button is not found
            except StaleElementReferenceException:
                continue  # Continue to the next iteration to search for the button again
            except Exception as e:
                break  # Exit the inner loop if another error occurs
            z +=1

        # Exit the outer loop if the button is no longer present
        if 'amscroll-load-button-new' not in driver.page_source:
            break    

##################################################################################
# 3) Gather all information for each food item in each subcategory
# List for all extracted data
product = []
sub = []
a = 0

# Helper function to avoid empty lists
def extract_text_or_na(elements):
    return [element.get_text(strip=True) for element in elements] if elements else [""]

# Ensure all lists are of the same length
def extend_to_max_length(lst, max_length):
    return lst + [""] * (max_length - len(lst))

# Iterate through each URL
for url in urls:
    # Send request to the website
    response = requests.get(url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all 'li' elements representing products
    li_items = soup.find_all('li', class_='item product product-item')

    # Extract product URLs
    product_urls = []
    for li in li_items:
        a_tag = li.find('a', class_='product-item-link')
        if a_tag:  # Ensure 'a_tag' is not None
            product_urls.append(a_tag['href'])
        sub.append(subcat[a])
    a +=1

    # Iterate through each product page URL and extract data
    for product_url in product_urls:
        response = requests.get(product_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data
        title = extract_text_or_na(soup.find_all('span', itemprop='name'))
        review = extract_text_or_na(soup.find_all('span', itemprop='reviewCount'))
        before_discount_price = extract_text_or_na(soup.find_all('del', class_='pricefield__old-price'))
        weight = extract_text_or_na(soup.find_all('span', class_='pricefield__footer'))
        brand = extract_text_or_na(soup.find_all('p', class_='brand-name'))
        art = extract_text_or_na(soup.find_all('p', class_='sku text-gray'))

        # Extract price (can be empty)
        price_tag = soup.find('strong', {'class': 'pricefield__price', 'itemprop': 'price'})
        selling_price = price_tag['content'] if price_tag and price_tag.has_attr('content') else ""
        discount = extract_text_or_na(soup.find_all('span', class_='pricefield__header'))
        origin = extract_text_or_na(soup.find_all('div', itemprop='description'))
        date = extract_text_or_na(soup.find_all('div', class_='ribbon__text'))

        # Ensure all lists are of the same length
        max_length = 1
        
        # Extend all lists to match the same length
        title = extend_to_max_length(title, max_length)
        review = extend_to_max_length(review, max_length)
        before_discount_price = extend_to_max_length(before_discount_price, max_length)
        weight = extend_to_max_length(weight, max_length)
        brand = extend_to_max_length(brand, max_length)
        art = extend_to_max_length(art, max_length)
        selling_price_list = extend_to_max_length([selling_price], max_length)
        discount = extend_to_max_length(discount, max_length)
        origin = extend_to_max_length(origin, max_length)
        date = extend_to_max_length(date, max_length)

        # Collect data
        product.append({
            'Title': title[0],
            'Review': review[0],
            'Weight': weight[0],
            'Price_before_discount': before_discount_price[0],
            'Discount': discount[0],
            'Price': selling_price_list[0],
            'Date': date[0],
            'Origin': origin[0],
            'Brand': brand[0],
            'Id': art[0],
            'Url': product_url
            })

##################################################################################
# 4) Create a DataFrame with all food items and save it
# Create DataFrame with Timestamp for collecting data.
df = pd.DataFrame(product)
df['Subcategory'] = sub
df['Date_collecting_data'] = pd.Timestamp.now()

# Current date for filename
current_date = datetime.now().strftime("%Y-%m-%d")

# Save the CSV file in the 'dataset' folder with date in filename
file_path = f"lidl_scraper_parser_{current_date}.csv"
df.to_csv(file_path, index=False, sep=";")
