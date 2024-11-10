# common/data_cleaner.py
import openai
import re
import os
from dotenv import load_dotenv


load_dotenv()
OPENAI_KEY = os.getent('OPENAI_KEY')

def clean_data(text):
    """Utility function to clean scraped data"""
    if text is None:  # Add a check to handle None values
        return None

    # Continue with cleaning if text is valid
    cleaned = text.strip().replace('\n', '').replace('\t', '')
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with a single space
    cleaned = cleaned.replace('\xa0', ' ')  # Handle non-breaking spaces
    cleaned = cleaned.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
    cleaned = cleaned.replace(' St\u00fcck', 'pc.').replace(' Stk.', 'pc.') # Replace .Stk and Stück mit pc.
    cleaned = cleaned.replace('Die Herkunftsangabe findest du auf der Verpackung in der Filiale.', 'multiple'   ) # Replace with multiple if Herkunftsangabe is on packaging
    cleaned = cleaned.replace('\/', '/')
    # Replace "2.\u2013" with "2.0" for prices
    cleaned = cleaned.replace('.\u2013', '')
    print(cleaned)
    return cleaned

def chatGPT_simplify_names(name):
    openai.api_key = OPENAI_KEY
    # Create a prompt for the ChatGPT API
    prompt = (
        f"Given the product name '{name}', return only the simplified name of the fruit or vegetable in German. "
        f"For example, if the input is 'Schweizer Rockit Äpfel 400g, SUISSE GARANTIE', "
        f"the output should be 'Äpfel'. Return only one word! Always return the plural form of the word!"
    )

    # Call the OpenAI Chat API for the response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract and return the simplified name
    simplified_name = response.choices[0].message['content'].strip()
    return simplified_name


def price_per_unit(price, amount):
    # Convert the amount to a consistent format for processing
    if 'pc' in amount.lower():
        unit = 'pc'
        quantity = float(amount.lower().replace('pc', '').strip() or 1)  # Default to 1 if no number specified
        price_per_unit = price / quantity
    elif 'kg' in amount.lower():
        unit = 'kg'
        quantity = float(amount.lower().replace('kg', '').strip() or 1)  # Default to 1 if no number specified
        price_per_unit = price / quantity
    elif 'g' in amount.lower():
        unit = 'kg'
        # Convert grams to kilograms if the unit is in grams
        quantity = float(amount.lower().replace('g', '').strip()) / 1000  # Convert g to kg
        price_per_unit = price / quantity

    else:
        raise ValueError("Unknown unit in amount")

    return (price_per_unit, unit)

    # Remove any white spaces and handle common formatting issues
    price_str = price_str.replace(" ", "").replace("\\", "")
    
    # Extract the price and unit using regular expressions
    match = re.match(r'([\d\.]+)\/(\d*)([a-zA-Z]+)', price_str)
    if not match:
        return 0
    price = float(match.group(1))
    quantity = match.group(2)  # This can be empty for units like 'stk'
    unit = match.group(3).lower()

    # Convert the price to price per kg based on the unit
    if unit == 'kg':
        return price, unit
    elif unit == 'g' and quantity:
        return price * (1000 / int(quantity)), 'kg'
    elif unit in ['stk', 'pc', 'pz']:
        return price, 'pc'  # Price per piece doesn't need conversion
    else:
        return 0