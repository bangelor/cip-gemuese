# common/data_cleaner.py

import re

def clean_data(text):
    """Utility function to clean scraped data"""
    if text is None:  # Add a check to handle None values
        return None

    # Continue with cleaning if text is valid
    cleaned = text.strip().replace('\n', '').replace('\t', '')
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with a single space
    cleaned = cleaned.replace('\xa0', ' ')  # Handle non-breaking spaces
    cleaned = cleaned.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")

    # Replace "2.\u2013" with "2.0" for prices
    cleaned = cleaned.replace('.\u2013', '')

    return cleaned

