from __future__ import absolute_import, division, print_function
import pandas as pd; import numpy as np;
import requests; import os.path;
import nltk as nltk
from nltk.corpus import stopwords; from nltk.cluster.util import cosine_distance; from nltk import pos_tag
from nltk.stem import WordNetLemmatizer; from nltk.tokenize import sent_tokenize, word_tokenize
import networkx as nx
from bs4 import BeautifulSoup
alt_stopwords = set(stopwords.words('english'))
wordlemmatizer = WordNetLemmatizer()

#Alternative implementation taken from here https://medium.com/voice-tech-podcast/automatic-extractive-text-summarization-using-tfidf-3fc9a7b26f5

def read_blogs():
    if os.path.exists("articles.xlsx"):
        print("Using preexisting excell sheet instead")
        df = pd.read_excel("articles.xlsx", index_col=0)
        print(df)
        for i in range(5):
            print("*")
        return df

    else:
        page_urls = ["cr-1-4", "cr-1-2"]
        print("Reading blogs this may take a while.")
        url_list, entry_dict = [], {} #list will be passed to another function to read sub pages
        for i in range(21): #Max value of CR
            page_urls.append("cr-{}".format(i+1)) #Automating target pages
        print(page_urls)

        for i in range(len(page_urls)): #Is currently set to the first 6 entries for speed
            address = "http://themonstersknow.com/tag/{}/".format(page_urls[i])
            file = requests.get(address)
            print(address)
            soup = BeautifulSoup(file.content, "html.parser")
            read_data = soup.find_all("div", class_="entry-content")
            #Needs to follow link found in <a > tag, so that complete page is shown
            b = 0 #Local Iterator
            for item in read_data:
                b = b + 1; x = b
                print(x, item.get_text(), "\n ", item.a)
                if item.a is None:
                    text_entry = item.get_text()
                    text_entry = text_entry.replace("\n", "")
                    entry_dict[str(item.strong.text)] =  text_entry #This should make keys and values that work without the need to manually assign them

                elif item.a is not None:
                    print(item.a.get("href"))
                    if "http://" not in item.a.get("href"):
                        pass
                    else:
                        url_list.append(item.a.get("href"))
        print("Reading sub lists")
        url_list, entry_dict = read_sublinks(url_list, entry_dict)

        url_list = list(dict.fromkeys(url_list))
        print("Testing: {}".format(url_list), "\n ")
        print("formed dictionary of articles ", entry_dict.keys())
        df = form_df(entry_dict)
        return df

def form_df(entry_dict):
    df_mk = pd.DataFrame(columns=["article_id", "text"])
    for k, v in sorted (entry_dict.items()):
        print(k, "is the key for: ", v)
        df_mk = df_mk.append({"article_id": k, "text": v}, ignore_index=True)
    form_sql(df_mk)
    df_mk.to_excel("articles.xlsx", sheet_name="monstersknow")
    return df_mk

def clean_text(df_targ):
    article = str(df_targ["text"].values)
    sections = article.split(".Next: ")
    text = str(sections[0])
    return text
def find_article():
    df = read_blogs()
    df = df.sample(1)
    target_text = clean_text(df)
    print(target_text)



find_article()