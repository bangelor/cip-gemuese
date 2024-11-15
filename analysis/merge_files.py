import numpy as np
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
import os
import csv


#read in the data from all stores

path_aldi = "C:\\Users\\41798\\Desktop\\CIP\\cip-gemuese\\aldi_transform.csv"

path_lidl = "C:\\Users\\41798\\Desktop\\CIP\\cip-gemuese\\lidl_transform.csv"

path_migros = "C:\\Users\\41798\\Desktop\\CIP\\cip-gemuese\\migros_scraper_parser_2024-11-11-Nov-19.csv"


#show all the observations from the first 5 rows

pd.options.display.max_columns = None
pd.options.display.max_rows = None

#read in the data
aldi_df = pd.read_csv(path_aldi, sep=",")
lidl_df = pd.read_csv(path_lidl, sep=";")
migros_df = pd.read_csv(path_migros, sep=";")

#checks the shape of the dataframe
print("aldi shape:", aldi_df.shape)
print("lidl_shape:", lidl_df.shape)
print("migros_shape:", migros_df.shape)


#check if the column names are the same
aldi_columns = set(aldi_df.columns)
lidl_columns = set(lidl_df.columns)
migros_columns = set(migros_df.columns)



#check for the intersection
#aldi dataframe is the template for column names
#check manually which difference in aldi_only_cols and lidl_only_cols could fit together
commen_cols = aldi_columns.intersection(lidl_columns)
print("common_cols:", commen_cols)
print("length common cols:",len(commen_cols))
aldi_only_cols = aldi_columns.difference(lidl_columns)
print("only aldi:", aldi_only_cols)
lidl_only_cols = lidl_columns.difference(aldi_columns)
print("only lidl:", lidl_only_cols)

#check difference between aldi and migros
print("*"*1000)
commen_cols = aldi_columns.intersection(migros_columns)
print("common_cols:", commen_cols)
print("length common cols:",len(commen_cols))
aldi_only_cols = aldi_columns.difference(migros_columns)
print("only aldi:", aldi_only_cols)
migros_only_cols = migros_columns.difference(aldi_columns)
print("only migros:", migros_only_cols)
print("*"*1000)

#in lidl change columns Origin-->country_origin, Subcategory--> sub_category, Store --> retailer
#rename the columns

lidl_df = lidl_df.rename(columns={
    "Origin": "country_origin",
    "Subcategory": "sub_category",
    "Store": "retailer"
})

#check again if the intersection shows 3 more columns lidl

#check if the column names are the same
aldi_columns = set(aldi_df.columns)
lidl_columns = set(lidl_df.columns)

commen_cols = aldi_columns.intersection(lidl_columns)
print("common cols:", commen_cols)
print("length common cols:", len(commen_cols))


###rename the migros dataset
###price_per_amount -->price per 100g/pice, store --> retailer, category --> main_categroy

print("*"*1000)
migros_df = migros_df.rename(columns={
    "price_per_amount": "price per 100g/pice",
    "category": "main_category",
    "store": "retailer"
})

#check if the column names are the same
aldi_columns = set(aldi_df.columns)
migros_columns = set(migros_df.columns)

commen_cols = aldi_columns.intersection(migros_columns)
print("common cols:", commen_cols)
print("length common cols:", len(commen_cols))

print("*"*1000)


#merge the dataset together
#keep the difference of the data

stores_combined_df = pd.concat([aldi_df.reset_index(drop=True), lidl_df.reset_index(drop=True), migros_df.reset_index(drop=True)], ignore_index=True)

#change the content in the common columns

#change yes/no to Wahr/Falsch in BIO column


stores_combined_df["BIO"] = stores_combined_df["BIO"].replace({
    "yes": "True",
    "no": "False",
    "True" : "true",
    "False": "False"
})

#change yes/no to Wahr/Falsch in BIO column

print(stores_combined_df["Swiss_product"])

stores_combined_df["Swiss_product"] = stores_combined_df["Swiss_product"].replace({
    "yes": "True",
    "no": "False",
    "True" : "true",
    "False": "False",
    "unknown": np.nan
})

#change the main category all to lower cases

stores_combined_df["main_category"] = stores_combined_df["main_category"].str.lower()

#change the gemuse --> gemüse, fruchte --> obst, obst-&-gemüse --> gemüse

stores_combined_df["main_category"] = stores_combined_df["main_category"].replace({"gemuse":"gemüse", "fruchte":"obst", "obst-&-gemüse":"gemüse"})

#change the time to only the date not with the daytime anymore

#only keeps the format yyyy-mm-dd
stores_combined_df["time"] = stores_combined_df["time"].str[:10]
#changes to the datetime format
stores_combined_df["time"] = pd.to_datetime(stores_combined_df["time"], errors='coerce').dt.date






print("rows in the merged file:" , len(stores_combined_df))
print("rows all files together calculated", len(migros_df) + len(lidl_df) + len(aldi_df))
"""
#splits the list into batches because chatgpt cant handle the whole list at once
def split_into_batches(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]






batch_size = 500
openai_lst = list(stores_combined_df["name"])
batches = list(split_into_batches(openai_lst, batch_size))

for batch in batches:
    print(batch)
    print(len(batch))
"""




"""
#splits the list into batches because chatgpt cant handle the whole list at once
def split_into_batches(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


#create a new column with a simple name

os.environ["OPENAI_API_KEY"] = "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"
chat = ChatOpenAI(model_name = "gpt-3.5-turbo")

#create a template for the prompt

prompt_template = PromptTemplate(
    input_variables=["product_list"],
    template= "Here is a list of fruits and vegetable:{product_list}."
              "please return a list without any other explanation for example"
              "'Schweizer Rockit Äpfel 400g, suisse garantie' should be only 'Apfel' return the list in this format ['Äpfel','Birnen','Bananen'...]"
              "only in the singular form"
              "most important that the input length of the list is equal to the output length of the list"


)


#function which handles the response of chatgpt

def list_returner(response:str) -> list:
    text = re.search(r'\[(.*?)]', response)
    match = text.group(1).replace("'","").split(",")
    print(match)
    return match


#creates chain
chain = LLMChain(llm=chat, prompt=prompt_template)


#chose batchsize has to be manually changed
#because
batch_size = 100
openai_lst = list(stores_combined_df["name"])
batches = list(split_into_batches(openai_lst, batch_size))


#creates a loop and saves the response of chatgpt in a list
filtered_responses = []


for batch in batches:
    print("this is the batch", batch)
    product_list_str = ", ".join(batch)
    response = chain.run(product_list=batch)
    print("this is the response", response)
    filtered_responses.extend(list_returner(response))
    print("this is the filtered response", filtered_responses)
    print(len(filtered_responses))


#checks the length of the list from the dataset and the response list
print("length list response", len(filtered_responses))
print("length list datset", len(openai_lst))
print(filtered_responses)

stores_combined_df["product_simple"] = filtered_responses

print(stores_combined_df["product_simple"])


#from common.data_cleaner import chatGPT_simplify_names
#chatGPT_simplyfy_names("produktname")

"""


os.environ["OPENAI_API_KEY"] = "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"
chat = ChatOpenAI(model_name = "gpt-3.5-turbo")

openai_lst = list(stores_combined_df["name"])

# Geht jedes Element einzeln durch und verwendet ChatGPT
filtered_responses = []

# Passe das Prompt für die Einzelverarbeitung an
prompt_template = PromptTemplate(
    input_variables=["product"],
    template="Here is a single fruit or vegetable: {product}."
             "Please return only its simplified name without any other explanation."
             "For example, 'Schweizer Rockit Äpfel 400g, suisse garantie' should be just 'Apfel'."
             "Make sure the input length matches the output length exactly, and provide only the singular form."
             "Return the result as a single string, not a list."
)

# Erstelle eine neue Chain für Einzelverarbeitung
chain = LLMChain(llm=chat, prompt=prompt_template)

# Verarbeite jedes Element
for product_name in openai_lst:
    print("Processing product:", product_name)

    # Übergebe das aktuelle Produkt an den Prompt
    response = chain.run(product=product_name)
    print("Response from ChatGPT:", response)

    # Füge das Ergebnis direkt zur Liste hinzu
    filtered_responses.append(response.strip())  # Entferne mögliche Leerzeichen
    print("Filtered response so far:", filtered_responses)
    print("Current length of filtered responses:", len(filtered_responses))

# Überprüfe die Längen
print("Length of response list:", len(filtered_responses))
print("Length of dataset list:", len(openai_lst))

# Füge die Ergebnisse als neue Spalte in das DataFrame ein
stores_combined_df["product_simple"] = filtered_responses

# Überprüfe die Ergebnisse
print(stores_combined_df["product_simple"])

#write the file

stores_combined_df.to_excel("C:\\Users\\41798\\Desktop\\CIP\\cip-gemuese\\stores_combined_all.xlsx", index=False)
stores_combined_df.to_csv("C:\\Users\\41798\\Desktop\\CIP\\cip-gemuese\\stores_combined_all.csv", index=False)



