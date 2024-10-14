# main.py
from stores.migros.migros_scraper import MigrosScraper
from storage.azure_blob_storage import AzureBlobStorage
import json

def scrape_migros_and_store():
    """Function to scrape and store Migros data"""
    scraper = MigrosScraper()
    scraped_data = scraper.scrape_and_parse()
    scraper.close()

    # Convert data to JSON
    json_data = json.dumps(scraped_data, indent=4)

    # Store the data in Azure Blob Storage
    azure_storage = AzureBlobStorage()
    azure_storage.upload_data(store_name= 'migros', data=json_data)

    print("Migros data scraped and stored in Azure Blob Storage.")

# Usage
if __name__ == "__main__":
    scrape_migros_and_store()
