# Packages
import pandas as pd
from datetime import datetime
import glob
import os
import numpy as np
import openai # openai==0.28.0
import config

# Combine several scraped data by finding all files that start with "lidl_scraper_parser_" and end with ".csv"
files = glob.glob(os.path.join( 'lidl_scraper_parser_*.csv'))

if len(files) == 1:
    # If there's only one file, read it directly without concatenation
    df = pd.read_csv(files[0], sep=';')
else:
    # If there are multiple files, read and concatenate them
    dataframes = [pd.read_csv(file, sep=';') for file in files]
    df = pd.concat(dataframes, ignore_index=True)

#####################################################################################################################
#Check for gaps / missing data
def check_missing_data(df):
    missing_data = df.isnull().sum()
    print("Missing data per column:\n", missing_data)
    return missing_data

df_na = check_missing_data(df)

def check_conditions(df):
    errors = []

    # Check conditions
    if df['Title'] != 0:
        errors.append("Title")
    if df['Review'] != 0:
        errors.append("Review")
    if df['Weight'] != 0:
        errors.append("Weight")
    if not (df['Price_before_discount'] == df['Discount'] == df['Date']):
        errors.append("Price_before_discount, Discount, Date")
    if df['Price'] != 0:
        errors.append("Price")
    if df['Url'] != 0:
        errors.append("Url")
    if df['Subcategory'] != 0:
        errors.append("Subcategory")
    if df['Date_collecting_data'] != 0:
        errors.append("Date_collecting_data")

    # See if there is an error
    if errors:
        print("Error found in column:", ", ".join(errors))
    else:
        print("No errors")
# All "must have" columns are clean. Some products does not have a brand or the origin is not given and known

check_conditions(df_na)
# Review NA = 0 - List Comprehension because '' is 0 and not unknown
# Review is not clean as "" is no Review and no Reviews means 0
df['Review'].fillna(0, inplace=True)

#####################################################################################################################
# Analyse dtypes
df.dtypes

# Date_collecting_data have wrong datatypes
# Timestamp - ensure correct datatype and generate a more suitalbe varialbe for comparison in the format Y-m-d
# Rename columns in more suitable variable
df['Date'] = ['' if df['Date'][i] == '' else df['Date'][i] for i in range(len(df))]
df.rename(columns={'Date': 'Timewindow_discount'}, inplace=True)
df['Date_collecting_data'] = pd.to_datetime(df['Date_collecting_data'], format="%Y-%m-%d %H:%M:%S.%f")
df['Date'] = df['Date_collecting_data'].dt.strftime('%Y-%m-%d')

#####################################################################################################################
# ID - Only extract the numbers after "Artikelnr.:"
df['Id'] = df['Id'].str.extract(r'(\d+)', expand=False)

# Origin - Standardization to unknown or already given Origin
def clean_origin(value):
    if pd.isna(value) or value == '' or value == 'diverse Sorten':
        return 'unknown'
    elif 'Herkunft:' in value:
        return value.split('Herkunft:')[1].strip()  # Split after "Herkunft:" and extract the text
    else:
        return value
# Apply function
df['Origin'] = df['Origin'].apply(clean_origin)

# Swiss Product - Function to compare if swiss product or not
def country_origin(value):
    if value == 'Schweiz':
        return 'True'
    elif value == 'unknown' or value =='Siehe Packung':
        return "unknown"
    else:
        return "False"
    
# Apply defined function
df['Swiss_Product'] = df['Origin'].apply(country_origin)

#####################################################################################################################
# Price before Discount and Discount - List Comprehension in order to substitute 'na' in Price with the value of 'Price before Discount'
df['Price_before_discount'] = [df['Price'][i] if df['Price_before_discount'][i] == '' else df['Price_before_discount'][i] for i in range(len(df))]
df['Discount_relative'] = ['' if df['Discount'][i] == '' else round(((df['Price_before_discount'][i]-df['Price'][i])/df['Price_before_discount'][i]),2) for i in range(len(df))]

# Descriptive mathematical Feature Engineering for price - higher then average
average_price = df['Price'].mean()
df['Price_higher_avg'] = df['Price'].apply(lambda x: "True" if x > average_price else "False")

# Analyse Price before discount (normal Price) regarding anchoring X.X9 in sense of 0.99CHF or 0.69 CHF
df['Last_char_price'] = df['Price'].astype(str).str[-1]
df['Is_last_char_9'] = df['Last_char_price'].apply(lambda x: 'True' if x == '9' else 'False')

#####################################################################################################################
# Ensure that the values within the Subcategory and in the range of Obst und Gemüse: Subcategory - Unsuitable subcategory "Hülsenfrüchte"
df['Subcategory_mod'] = ['Obst' if df['Subcategory'][i] == 'Hülsenfrüchte' else df['Subcategory'][i] for i in range(len(df))]

# Title: extract Bio for standardization purpose and the research question
df['Bio'] = df['Title'].str.contains('bio', case=False, na=False).map({True: 'True', False: 'False'})

# Title: New column Word_count as a nice have to analyze the title for example for NLP or branding strategy
df['Word_count'] = df['Title'].apply(lambda x: len(x.split()) if x else 0)

#####################################################################################################################
# Weight - Extract Unit from Weight due to the not standardized format
weight_piece_1 = df['Weight'].str.split('|').apply(lambda x: x[0]).tolist()
weight_piece_2 = pd.DataFrame({"W":weight_piece_1})['W'].str.split('pro' or '').apply(lambda x: x[-1]).tolist()
df['Unit'] = pd.DataFrame({"W":weight_piece_2})['W'].str.split().apply(lambda x: x[0]).tolist()

# Function for improving comparison Stück & g/kg
def convert_unit(value):

    # Remove empty value for safety reason
    value = value.replace(' ', '')

    # Transformation from 'Stk' to 'Stücke'
    if 'Stk' in value:
        numeric_part = value.replace('Stk.', '').replace(',', '.')
        if numeric_part:
            return f"{numeric_part} Stücke"
        return "Stücke"
    
    # Transformation for 'Stück' to '1 Stück', it there is no number in plural
    elif 'Stück' in value:
        numeric_part = value.replace('Stück', '').replace(',', '.')
        if numeric_part:
            return f"{numeric_part} Stück"
        return "1 Stück"

    # Standardization for the unit from 'kg' to g
    elif 'kg' in value:
        numeric_part = value.replace('kg', '').replace(',', '.')
        # If there is no number then 100g as there is just one kg
        if not numeric_part:
            return "1000g"
        # if there is additionally a number, then multiply and adding g
        return f"{float(numeric_part) * 1000:.0f}g"
    
    # Standardization for the unit g
    elif 'g' in value:
        numeric_part = value.replace('g', '').replace(',', '.')
        if numeric_part:
            return f"{float(numeric_part):.0f}g"  # 'g' hinzufügen
    
    # Return "Stücke" if there is a plural of objects
    elif value.isdigit():
        return f"{value} Stücke"

    # Return None if no valid value
    return None

# Apply function on 'Unit'
df['Clean_unit'] = df['Unit'].apply(convert_unit)

#####################################################################################################################
# Function for calculation, if "Stück" in given column
def calculate_price(row):
    if 'Stück' in row['Clean_unit']:
        # Split texts by ' '
        split_values = row['Clean_unit'].split(' ')
        try:
            # Extract the first value from number to "Stück"
            num_value = float(split_values[0])
        except ValueError:
            # If there is no number then 1
            num_value = 1
        
        # Calculation of the new prices with round
        return str(round(row['Price'] / (num_value),2))
    
        # Return price for Unit g
    elif 'g' in row['Clean_unit']:
        # Split texts by ' '
        split_values = row['Clean_unit'].split('g')
        try:
            # Extract the values
            num_value = float(split_values[0])
        except ValueError:
            # Add 1 if there is no number before Stücke
            num_value = 1
        
        # Calculation of new Price
        return str(round((row['Price'] / (num_value))*100,2))
    else:
        # If there is no piece (Stück), then return original value without transformation
        return row['Price']

# Apply the function on the calculated_price - either per 100g or per piece (Stück)
df['Calculated_price_per100g_perStück'] = df.apply(calculate_price, axis=1)
df['Weight_unit'] = df['Clean_unit'].str.contains('g', case=False, na=False).map({True: 'g', False: 'Stück'})

#####################################################################################################################
# Discount New Feature for Discount
df[['Start', 'End']] = df['Timewindow_discount'].str.split('-', expand=True)

# Clean the new variable start and end
df['Start'] = df['Start'].apply(lambda x: x.strip().replace(' ', '') if pd.notna(x) else x)
df['End'] = df['End'].apply(lambda x: x.strip().replace(' ', '') if pd.notna(x) else x)

# Adding 24 for discount date
today= datetime.today()
short = today.strftime('%y')

df['Discount_start_date'] = df['Start'].apply(lambda x: x + short if pd.notna(x) and x.strip() != '' else None)
df['Discount_end_date'] = df['End'].apply(lambda x: x + short if pd.notna(x) and x.strip() != '' else None)

# Drop not needed columns anymore
df.drop(['Start', 'End'], axis=1, inplace=True)

#####################################################################################################################
# Transform datatype in order for computation after the duration of Discount
df['Discount_start_date'] = pd.to_datetime(df['Discount_start_date'], format='%d.%m.%y', errors='coerce')
df['Discount_end_date'] = pd.to_datetime(df['Discount_end_date'], format='%d.%m.%y', errors='coerce')
df['Discount_end_date'] = df.apply(lambda row: row['Discount_end_date'].replace(year=row['discount_end_date'].year + 1)

# If the discount begins end of year and last for some days/week beyond new year, then this should be considered
if row['Discount_start_date'] > row['Discount_end_date'] else row['Discount_end_date'], axis=1)

# Name of day regarding Discount
df['Discount_start_day'] = df['Discount_start_date'].dt.day_name()
df['Discount_end_day'] = df['Discount_end_date'].dt.day_name()
df['Discount_duration'] = df['Discount_end_date'] - df['Discount_start_date']

# NA & Dummy Variable for Discount available or not
df  = df.fillna("")
df['Discount_exist'] = df.Discount.apply(lambda x: 'False' if x == "" else "True")

#####################################################################################################################
# Adding the store for comparing after merge
df["Store"] = "lidl"

#####################################################################################################################
# Column name for merging/combine aggregate regarding project scope
df.rename(columns={'Price': 'price'}, inplace=True)
df.rename(columns={'Clean_unit': 'amount'}, inplace=True)
df.rename(columns={'Calculated_price_per100g_perStück': 'price per 100g/pice'}, inplace=True)
df.rename(columns={'Subcategory_mod': 'main_category'}, inplace=True)
df.rename(columns={'Bio': 'BIO'}, inplace=True)
df.rename(columns={'Swiss_Product': 'Swiss_product'}, inplace=True)
df.rename(columns={'store': 'retailer'}, inplace=True)
df.rename(columns={'Date_collecting_data': 'time'}, inplace=True)

# Standardization name for comparing different products
# Using API Key which is in config file (gitignore)
def chatGPT_simplify_names(name):
    openai.api_key = config.OPENAI_API_KEY # please put here your api key if you want generating the prompts
    # Create a prompt for the ChatGPT API
    prompt = (
        f"Gib basierend auf dem Produktnamen eines Lebensmittelladens nur den vereinfachten Namen der Frucht oder des Gemüses auf Deutsch in der Pluralform zurück. "
        f"Stelle sicher, dass die Ausgabe nur ein einziges Wort ist, ohne Präfixe oder Suffixe. Zum Beispiel: "
        f"- Wenn der Input 'Schweizer Rockit Äpfel 400g, SUISSE GARANTIE' ist, sollte die Ausgabe 'Äpfel' sein. "
        f"- Wenn der Input 'Avocado' ist, sollte die Ausgabe 'Avocados' sein (ohne zusätzliche Wörter). "
        f"Gib nur die Pluralform als einzelnes Wort zurück, ohne zusätzlichen Text oder Erklärungen."
        f"Der Produktname zum prozessieren ist {name}"
    )

    # Call the OpenAI Chat API for the response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract and return the simplified name and replace "." if as hallucination generated
    simplified_name = response.choices[0].message['content'].strip()
    simplified_name = simplified_name.replace('.', '')

    return simplified_name

df['name'] = df['Title'].apply(chatGPT_simplify_names)

#####################################################################################################################
# Checking regarding outliers: there should be only one word in the new column name
def check_and_replace_outliers(df, column):

    # Count the number of words and replace entries if there are more than one word
    df['word_count'] = df[column].apply(lambda x: len(str(x).split()))
    df['is_outlier'] = df['word_count'] > 1
    df.loc[df['is_outlier'], column] = 'not clear'

    # Remove the 'word_count' and 'is_outlier' columns to keep the original DataFrame clean
    df.drop(['word_count', 'is_outlier'], axis=1, inplace=True)
    return df

df_final = check_and_replace_outliers(df, 'name')

#####################################################################################################################
# Save transformed dataframe as csv-file with the date of transformation
file_path = f"lidl_transform.csv"
df_final.to_csv(file_path, index=False, sep=";")
