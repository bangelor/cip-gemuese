# Packages
import pandas as pd
import numpy as np
from datetime import datetime
import glob
import os

# Define the folder path
folder_path = 'dataset_lidl/'

# Find all files that start with "lidl_scraper_parser_" and end with ".csv"
files = glob.glob(os.path.join(folder_path, 'lidl_scraper_parser_*.csv'))

if len(files) == 1:
    # If there's only one file, read it directly without concatenation
    df = pd.read_csv(files[0], sep=';')
        
else:
    # If there are multiple files, read and concatenate them
    dataframes = [pd.read_csv(file, sep=';') for file in files]
    df = pd.concat(dataframes, ignore_index=True)
    
    #Saving
    os.makedirs("../../../testingcip/dataset_lidl", exist_ok=True)
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_path = f"dataset_lidl/lidl_combined_{current_date}.csv"
    df.to_csv(file_path, index=False, sep=";")



# 1) ID - Nur die Zahlen nach "Artikelnr.:" extrahieren
df['Id'] = df['Id'].str.extract(r'(\d+)', expand=False)

# 2) Origin - Standardization
def clean_origin(value):
    if pd.isna(value) or value == '' or value == 'diverse Sorten':
        return 'unbekannt'
    elif 'Herkunft:' in value:
        return value.split('Herkunft:')[1].strip()  # Text nach "Herkunft:" extrahieren
    else:
        return value
    # Column wragling
df['Origin'] = df['Origin'].apply(clean_origin)

# Switzerland or not
def country_origin(value):
    if value == 'Schweiz':
        return 'yes'
    elif 'unbekannt' in value:
        return "unbekannt"  # Text nach "Herkunft:" extrahieren
    else:
        return "no"
    
# Column wragling
df['Swiss_Product'] = df['Origin'].apply(country_origin)

# 3) Review NA = 0
df['Review'] = [0 if x == '' else x for x in df['Review']]

# 4) Price before Discount: List Comprehension, um 'na' in Price durch den Wert aus 'Price before Discount' zu ersetzen
df['Price_before_discount'] = [df['Price'][i] if df['Price_before_discount'][i] == '' else df['Price'][i] for i in range(len(df))]
df['Discount'] = ['' if df['Discount'][i] == '' else df['Discount'][i] for i in range(len(df))]

# 5) Date NA
df['Date'] = ['' if df['Date'][i] == '' else df['Date'][i] for i in range(len(df))]

# 6) Brand NA
df['Brand'] = ["" if x == '' else x for x in df['Brand']]

# 7) Bio Standardization
df['Bio'] = df['Title'].str.contains('bio', case=False, na=False).map({True: 'yes', False: 'no'})

# 8) Timestamp - ensure correct datatype
df['Date_collecting_data'] = pd.to_datetime(df['Date_collecting_data'], format="%Y-%m-%d", errors='coerce')

# 9) New columns Count Word in Title
df['Word_count'] = df['Title'].apply(lambda x: len(x.split()) if x else 0)


# 10) Standardisierung Weight & New Columns 
weight_piece_1 = df['Weight'].str.split('|').apply(lambda x: x[0]).tolist()
weight_piece_2 = pd.DataFrame({"W":weight_piece_1})['W'].str.split('pro' or '').apply(lambda x: x[-1]).tolist()
df['Unit'] = pd.DataFrame({"W":weight_piece_2})['W'].str.split().apply(lambda x: x[0]).tolist()

# 11) Funktion zur Standardisierung der Einheiten
def convert_unit(value):
    # Entfernen von Leerzeichen zur Sicherheit
    value = value.replace(' ', '')
    
    # Umwandlung für 'Stk' zu 'Stücke'
    if 'Stk' in value:
        numeric_part = value.replace('Stk.', '').replace(',', '.')
        if numeric_part:
            return f"{numeric_part} Stücke"
        return "Stücke"
    
    # Umwandlung für 'Stück' zu '1 Stück', falls keine Zahl davor steht
    elif 'Stück' in value:
        numeric_part = value.replace('Stück', '').replace(',', '.')
        if numeric_part:
            return f"{numeric_part} Stück"
        return "1 Stück"

    # Standardisierung von Einheiten mit 'kg'
    elif 'kg' in value:
        numeric_part = value.replace('kg', '').replace(',', '.')
        # Falls keine Zahl vor 'kg' steht, gib 1000g zurück
        if not numeric_part:
            return "1000g"
        # Falls eine Zahl vorhanden ist, multipliziere mit 1000 und füge 'g' hinzu
        return f"{float(numeric_part) * 1000:.0f}g"
    
    # Standardisierung von Einheiten mit 'g'
    elif 'g' in value:
        numeric_part = value.replace('g', '').replace(',', '.')
        if numeric_part:
            return f"{float(numeric_part):.0f}g"  # 'g' hinzufügen
    
    # Falls nur eine Zahl vorhanden ist, zu 'Stücke' umwandeln
    elif value.isdigit():
        return f"{value} Stücke"
    # Falls der Wert ungültig ist, None zurückgeben
    return None

# Anwenden der Funktion auf die Spalte 'unit'
df['clean_unit'] = df['Unit'].apply(convert_unit)

# Funktion für die Berechnung, wenn "Stück" in der Spalte 'x' vorkommt
def calculate_price(row):
    if 'Stück' in row['clean_unit']:
        # Splitten des Textes in Spalte 'x' nach Leerzeichen
        split_values = row['clean_unit'].split(' ')
        try:
            # Extrahiere den ersten Wert aus dem Split (Zahl vor "Stück")
            num_value = float(split_values[0])
        except ValueError:
            # Wenn keine Zahl vor "Stück" steht, standardmäßig 1 verwenden
            num_value = 1
        
        # Berechnung des neuen Preises: y / (1 / num_value)
        return str(round(row['Price'] / (num_value),2))
    
        # Wenn kein "Stück" vorhanden ist, den Originalwert von 'y' zurückgeben
    elif 'g' in row['clean_unit']:
        # Splitten des Textes in Spalte 'x' nach Leerzeichen
        split_values = row['clean_unit'].split('g')
        try:
            # Extrahiere den ersten Wert aus dem Split (Zahl vor "Stück")
            num_value = float(split_values[0])
        except ValueError:
            # Wenn keine Zahl vor "Stück" steht, standardmäßig 1 verwenden
            num_value = 1
        
        # Berechnung des neuen Preises: y / (1 / num_value)
        return str(round((row['Price'] / (num_value))*100,2))
    else:
        # Wenn kein "Stück" vorhanden ist, den Originalwert von 'y' zurückgeben
        return row['Price']

# Anwenden der Funktion auf die Zeilen des DataFrames
df['calculated_price_per100g_perStück'] = df.apply(calculate_price, axis=1)
df['Weight_unit'] = df['clean_unit'].str.contains('g', case=False, na=False).map({True: 'g', False: 'Stück'})


# 12) Discount New Feature for Discount 
df[['start', 'ende']] = df['Date'].str.split('-', expand=True)

# Bereinigen der Spalten 'start' und 'ende' von führenden/nachfolgenden Leerzeichen und überflüssigen Leerzeichen
df['start'] = df['start'].apply(lambda x: x.strip().replace(' ', '') if pd.notna(x) else x)
df['ende'] = df['ende'].apply(lambda x: x.strip().replace(' ', '') if pd.notna(x) else x)

# Setze nur die neuen Spalten, wenn 'start' und 'ende' nicht leer sind oder nicht nur leere Strings enthalten
df['discount_start_date'] = df['start'].apply(lambda x: x + '24' if pd.notna(x) and x.strip() != '' else None)
df['discount_ende_date'] = df['ende'].apply(lambda x: x + '24' if pd.notna(x) and x.strip() != '' else None)

# Unnötige Spalten entfernen (optional)
df.drop(['start', 'ende'], axis=1, inplace=True)

# Transform datatype in order for compution after the durcation of Discount
df['discount_start_date'] = pd.to_datetime(df['discount_start_date'], format='%d.%m.%y', errors='coerce')
df['discount_ende_date'] = pd.to_datetime(df['discount_ende_date'], format='%d.%m.%y', errors='coerce')
df['discount_ende_date'] = df.apply(lambda row: row['discount_ende_date'].replace(year=row['discount_ende_date'].year + 1) 
if row['discount_start_date'] > row['discount_ende_date'] else row['discount_ende_date'], axis=1)

# Name of Day regarding Discount
df['discount_start_day'] = df['discount_start_date'].dt.day_name()
df['discount_ende_day'] = df['discount_ende_date'].dt.day_name()
df['Discount_duration'] = df['discount_ende_date'] - df['discount_start_date']

# NA & Dummy Variable for Discount available or not
df  = df.fillna("")
df['Discount_exist'] = df.Discount.apply(lambda x: 'no' if x == "" else "yes")

# 13) DataFrame erstellen und speichern
os.makedirs("../../../testingcip/dataset_lidl", exist_ok=True)
current_date = datetime.now().strftime("%Y-%m-%d")
file_path = f"dataset_lidl/lidl_transform_{current_date}.csv"
df.to_csv(file_path, index=False, sep=";")

