# common/data_cleaner.py
def clean_data(text):
    """Utility function to clean scraped data"""
    return text.strip().replace('\n', '').replace('\t', '')
