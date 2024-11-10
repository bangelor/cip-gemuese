# common/data_cleaner.py
import openai
import re
import os
from dotenv import load_dotenv


load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_KEY')

def clean_data(text):
    """Utility function to clean scraped data"""
    if text is None:  # Add a check to handle None values
        return None

    # Continue with cleaning if text is valid
    cleaned = text.strip().replace('\n', '').replace('\t', '')
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with a single space
    cleaned = cleaned.replace('\xa0', ' ')  # Handle non-breaking spaces
    cleaned = cleaned.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
    cleaned = cleaned.replace(' St\u00fcck', 'pc').replace(' Stk.', 'pc').replace('pc.', 'pc') # Replace .Stk and Stück mit pc.
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
        f"Gib basierend auf dem Produktnamen eines Lebensmittelladens nur den vereinfachten Namen der Frucht oder des Gemüses auf Deutsch in der Pluralform zurück. "
        f"Stelle sicher, dass die Ausgabe nur ein einziges Wort ist, ohne Präfixe oder Suffixe. Zum Beispiel: "
        f"- Wenn der Input 'Schweizer Rockit Äpfel 400g, SUISSE GARANTIE' ist, sollte die Ausgabe 'Äpfel' sein. "
        f"- Wenn der Input 'Avocado' ist, sollte die Ausgabe 'Avocados' sein (ohne zusätzliche Wörter). "
        f"Gib nur die Pluralform als einzelnes Wort zurück, ohne zusätzlichen Text oder Erklärungen."
        f"Der Produkname zum prozessieren ist {name}"
    )

    # Call the OpenAI Chat API for the response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
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
        print("Unknown unit in amount, returning NA")
        unit = "NA"
        price_per_unit = "NA"
    return (price_per_unit, unit)