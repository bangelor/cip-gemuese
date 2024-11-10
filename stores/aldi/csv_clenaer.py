import pandas as pd
import numpy as np
import csv
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
import glob

#define the directory path where the csv files are located in
directory_path = "C:\\Users\\41798\\Desktop\\CIP\\cip-gemuese\\storage"

#get all the paths from all csv files in this directory
all_csv_files = glob.glob(os.path.join(directory_path, "*.csv"))

#create a empty list to collect the
dataframe_list = []

for file in all_csv_files:
    df = pd.read_csv(file)
    dataframe_list.append(df)

#concatinate all dataframes together
aldi_df = pd.concat(dataframe_list, ignore_index=True)


#show all the observations from the first 5 rows

pd.options.display.max_columns = None
pd.options.display.max_rows = None


#information about the file
aldi_df.info()

#show all the observations from the first 5 rows

pd.options.display.max_columns = None
pd.options.display.max_rows = None
print(aldi_df)


#create a column for BIO products yes or no

aldi_df["BIO"] = aldi_df["name"].str.contains("BIO", case= False, na=False)
print(aldi_df["BIO"])


#create a column with the prices for 100g or pice
#there are columns with per 1kg has to be divided by 10 and only the number has to be
#if the price is already per pice or per 100g only the float in the string will be extracted

aldi_df["price per 100g/pice"] = np.where(
    aldi_df["price_per_amount"].str.contains("1kg", case=True),
    aldi_df["price_per_amount"].str.split("/").str[0].astype(float)/10,
    aldi_df["price_per_amount"].str.split("/").str[0].astype(float)
)

print(aldi_df)

#create a column which tells if the product is from Switzerland or not
#for NAN there will be also NAN


aldi_df["Swiss_product"] = aldi_df["country_origin"].str.contains("Schweiz", case=True, na=np.nan)
print(aldi_df)

os.environ["OPENAI_API_KEY"] = "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"


#the column with all the name description in the product will be saved as an list

openai_lst = list(aldi_df["name"])


"""

#create a template for the prompt

prompt_template = PromptTemplate(
    input_variables=["product_list"],
    template= "Here is a list of fruits and vegetable:{product_list}."
              "please return a list with only the names of the fruits or vegetables for example"
              "'Schweizer Rockit Äpfel 400g, suisse garantie' should be only 'Äpfel' return the list in german and in the same format please"
              "if possible only in the plural form"

)



chat = ChatOpenAI(model_name = "gpt-4")

chain = LLMChain(llm=chat, prompt=prompt_template)

response = chain.run(product_list=openai_lst)


#create a function which only replies the list from chatgpt

def list_returner(response):
    text = re.search(r'\[(.*?)]', response)
    match = text.group(1).replace("'","").split(",")
    return match


filtered_response = list_returner(response)

print(len(filtered_response))
print(filtered_response)

aldi_df["product_simple"] = filtered_response

"""

#create a column with the retailer

aldi_df["retailer"] = "aldi"

#separate the category to category and subcategory

aldi_df[["main_category", "sub_category"]] = aldi_df["category"].str.split("/", expand = True)

#write the new excel data

filename_csv = f"aldi_transform.csv"
directory = "C:\\Users\\41798\\Desktop\\CIP\\cip-gemuese\\storage\\"
full_path_csv = os.path.join(directory,filename_csv)

aldi_df.to_csv(full_path_csv, index=False)

