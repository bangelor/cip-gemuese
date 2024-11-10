# main.py
from stores.migros.migros_scraper import MigrosScraper
from storage.azure_blob_storage import AzureBlobStorage
from stores.aldi.ALDI_SCRAPER import AldiScraper
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

def scrape_aldi_and_store():
    """Function to scrape and store Aldi data"""
    scraper = AldiScraper()
    scraped_data = scraper.scrape(url="https://www.aldi-now.ch/de/obst-&-gem%C3%BCse?ipp=36")
    scraper.close()

    if scraped_data is not None:
        # Convert data to JSON
        json_data = scraped_data.to_json(orient='records', indent=4)

        # Store the data in Azure Blob Storage
        azure_storage = AzureBlobStorage()
        azure_storage.upload_data(store_name='aldi', data=json_data)
    print("Aldi data scraped and stored in Azure Blob Storage.")


# Usage
if __name__ == "__main__":
    scrape_migros_and_store()
    scrape_aldi_and_store()