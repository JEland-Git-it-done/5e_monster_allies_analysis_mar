import pandas as pd; import numpy as np;
import requests; import os; import re; import json
from bs4 import BeautifulSoup
from transliterate import translit, detect_language; import time; from alphabet_detector import AlphabetDetector






#This addon pack focuses on the application of current and historic data to create more organic naming conventions for NPC's
#The following dataset will act as an anchor for this https://www.ssb.no/en/navn#renderAjaxBanner
#https://www.europeandataportal.eu/data/datasets?locale=en&tags=vornamen&keywords=vornamen
#Changed idea to read wikipedia pages eg. https://en.wikipedia.org/w/index.php?title=Category:German-language_surnames&pagefrom=Eschenbach%0AEschenbach+%28surname%29#mw-pages
#https://archaeologydataservice.ac.uk/archives/view/atlas_ahrb_2005/datasets.cfm?CFID=331341&CFTOKEN=70517262
#Any information taken from https://www.europeandataportal.eu is being used under the Creative Commons Share-Alike Attribution Licence (CC-BY-SA), none is currently being used.
#Arcane name set seems like a useful idea, see text below
#Look into GeoNames dataset found here, https://github.com/awesomedata/awesome-public-datasets , could be used for expanded town name generator
#Possible use argument for this dataset https://github.com/smashew/NameDatabases/tree/master/NamesDatabases
#Use in conjunction with the place names loaded by geonames
'''
Courtesy of u/Alazypanda -
If need random fantastical sounding names I quite literally take the "generic" or chemical names of medication
Like the leader of the mafia my players are working with, Levo Thyroxine.
Might be worth adding some to the data base, but then its up to you to find where to split the word for first/lastname to make it sound right.

Wikientries are now being used to form "organic" lists, the problem with these entries is that they are usually using seperate formats from 
one another, meaning that there is no standardised function that i can create to pass each link through
'''

def italian_surnames(): #This function is a test case of reading a wikipedia list to source names, with the names being loaded in DL elements (descriptive lists)
    file = requests.get("https://en.wiktionary.org/wiki/Appendix:Italian_surnames")
    soup = BeautifulSoup(file.content, "html.parser")
    rec_data = soup.find_all("li")
    df = pd.DataFrame(columns=["name", "tag", "origin"])
    for item in rec_data:
        if item.string == "Zullo":#This is the final part of the page, is used to exit loop
            adder = str(item.string)
            df = df.append({"name": adder, "tag": "S", "origin": "ITA"}, ignore_index=True)
            break
        if item.string is not None:
            adder = str(item.string)
            df = df.append({"name": adder, "tag": "S", "origin": "ITA"}, ignore_index=True)  # S tag is indicative of the surname
    df["name"] = df["name"].str.replace("[^\w\s]", "")
    print(df.tail(60))
    return df


def soup_surnames():
    #is_valid = False
    if os.path.exists("surnames_cleaned_complete.xlsx"):
        #Implements checks
        df = pd.read_csv("surnames_cleaned.xlsx")
        non_valid_names = df.loc[df["name"].str.contains("Appendix|learn more|previous", na=False)]
        df.drop(non_valid_names, inplace=True)
        print(df)
        print(pd.unique(df["name"]))
        return df
    else:
        print("Starting Soup")
        df = pd.DataFrame(columns=["name", "tag", "origin"])
        bins = ["Asian", "African", "European", "Iberian", "Russian", "Caucausus", "Balkan"]
        surname_urls = read_surnames()
        #print("Surname arguments are as follows: ", surname_urls)
        for key, value in surname_urls.items():
            try:
                if "-" in key:
                    nationality = key.split("-")[0]
                else:
                    nationality = key.split(" ")[0]
            except:
                pass
            print(key, value)
            if value == 'https://en.wiktionary.org/wiki/Category:Surnames_by_language':
                #Wiktionary names are in their original language, need to follow deeper to find the english prounouncation
                key_format = "https://en.wiktionary.org/wiki/Category:{}".format(key)
                wiktionary_page = "https://en.wiktionary.org"
                #if key == "Arabic surnames" or key == "Persian surnames":
                df = read_wiki(df, key_format, nationality.strip(), wiktionary_page)


            elif value == 'https://en.wikipedia.org/wiki/Category:Surnames_by_language':

                key_format = "https://en.wikipedia.org/wiki/Category:{}".format(key)
                wiki_page = "https://en.wikipedia.org"
                df = read_wiki(df, key_format, nationality.strip(), wiki_page)
                #file = requests.get("https://en.wiktionary.org/wiki/Category:{}".format(key))
                #print(file_url)
                #soup = BeautifulSoup(file.content, "html.parser")
        #Clean out dataframe
        print("Printing dataframe: \n\n\n", df)
        df.to_excel("surnames_cleaned.xlsx", index=False)
        print(df)
        print(pd.unique(df["name"]))
        big_list = pd.unique(df["name"])
        print(list(big_list))
        return df

def read_wiki(df, key, origins, page_type):
    if page_type == "https://en.wiktionary.org":
        problem_list = ["Arabic", "Hindi", "Persian", "Hebrew", "Telugu", "Chinese", "Japanese", "Korean"]
        print("Value is from Wiktionary")
        print("Looking for english variatey")
        file = requests.get(key)
        soup = BeautifulSoup(file.content, "html.parser")
        div_tag = soup.find_all("div", {"id": "mw-pages"})
        for tag in div_tag:
            list_tag = tag.find_all("li")
            for name in list_tag:
                print(name,"\n", origins)
                if origins not in problem_list:
                    print("This name is using translatable characters")
                    split_name = name.string.split(" ")[0]  # Incase of any disambiguations or other issues
                    print(split_name)
                    if any(re.findall(r"Appendix|learn more|previous", split_name, re.IGNORECASE)):
                        print("Invalid name: ", split_name)
                    else:
                        df = df.append({"name": split_name, "tag": "N", "origin": origins}, ignore_index=True)
                elif origins in problem_list:
                    print(name.string.split(" ")[0], origins)
                    split_name = find_latin_name(page_type, name.a["href"])
                    print("English version of name: {}".format(split_name))
                    df = df.append({"name": split_name, "tag": "N", "origin": origins}, ignore_index=True)
        return df
    elif page_type == "https://en.wikipedia.org":
        print("Value is from Wikipedia")
        file = requests.get(key)
        soup = BeautifulSoup(file.content, "html.parser")
        # First things first the soup needs to search if there is a next page
        div_tag = soup.find_all("div", {"id": "mw-pages"})
        for tag in div_tag:
            list_tag = tag.find_all("li")
            for name in list_tag:
                name = name.string.split(" ")[0] #Incase of any disambiguations or other issues
                print(name,"\n", origins)
                if any(re.findall(r"Appendix|learn more|previous", name, re.IGNORECASE)):
                    print("Invalid name: ", name)
                else:
                    df = df.append({"name": name, "tag": "N", "origin": origins}, ignore_index=True)
            a_tag = tag.find_all("a", href=True)
            print(a_tag[0].string)
            for a_link in a_tag:
                if "next page" in a_link.string:
                    print("There is a page in the tag: https://en.wiktionary.org{}".format(a_link["href"]))
                    df = read_wiki(df, page_type + a_link["href"], origins, page_type)
                    break

        return df

def find_latin_name(page, link):
    names = []
    possible_tags = ["headword-tr manual-tr tr Latn", "headword-tr tr Latn"]
    file = requests.get(page+link)
    soup = BeautifulSoup(file.content, "html.parser")

    for i in possible_tags:
        try:
            span_tag = soup.find_all("span", {"class": i})
            names = span_tag[0].string.strip("()")
        except:
            pass
    return names


def read_surnames():
    #https://en.wiktionary.org/wiki/Category:Surnames_by_language
    #This function aims to go through each of the catagories listed in the above link, goes through each entry and tries to assign them to one of the pre existing lists
    print("Attempting to webscrape surnames, along with some straggeler forenames")
    #The following names are relatively populated
    valid_names = {}
    files = ["https://en.wiktionary.org/wiki/Category:Surnames_by_language", "https://en.wikipedia.org/wiki/Category:Surnames_by_language"]
    for file_url in files:
        file = requests.get(file_url)
        print(file_url)
        soup = BeautifulSoup(file.content, "html.parser")
        div_tag = soup.find_all("div", {"class": "CategoryTreeItem"})
        for article in div_tag:
            #print(article)
            #print(file_url)
            span_tag = article.find_all("span", {"dir": "ltr"})[0] #The first span element with this tag holds the length of the article
            if "," in span_tag.string:
                span_checker = span_tag.string.split(",", 1)[1]
            else:
                span_checker = span_tag.string

            span_checker = re.sub('[^0-9]','', span_checker)
            if int(span_checker) >= 25:
                valid_names.update({article.a.text: file_url})
                #print("Valid names include: ", valid_names)
            #print(span_checker)
            #print(article, article.a, "\n\n{}".format(article.a.text))
        #print(valid_names)
    print(valid_names)
    return valid_names

def splice_names():
    #Please note that most of the names involved in this function are infact latin-ised names, and cover countries that have already been found via web scraping
    df = form_international_names()
    df_bs4 = form_latin_name_dict()

    frames = [df, df_bs4]
    df_merge = pd.concat(frames)
    df_merge.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)
    df_merge.to_excel("firstnames_merged.xlsx", index=False)
    #print(df_merge)

    print("Checking if name exists more than once")
    counts = df["origin"].value_counts()
    counts = df[df["origin"].isin(counts.index[counts.gt(2)])]
    #print(counts)
    print(counts.tail(40))

    return df_merge



def form_international_names(): #add npc_df as argument
    #Due to a distinct lack of international names, outside of europe from the previous sources
    #This function will use the first name database provided by Matthias Winkelmann and Jörg MICHAEL at the following address
    #https://github.com/MatthiasWinkelmann/firstname-database

    exists = check_if_exists()
    add_files = False #Default value
    decision = start_soup(add_files)
    print(decision)

    if exists and decision is False:
        print("This file already exists in the a already created CSV folder, this function will use this version instead of creating a new file")
        df = pd.read_excel("firstnames_cleaned.xlsx")
        new_df = df
        make_cross_compatible(new_df)

        print(pd.unique(new_df["tag"]))
        return new_df
    elif not exists or decision is True:
        print("Splicing previous dataframe with international dataframe")
        df_target = pd.read_csv("firstnames_matthiaswinkelmann.csv")
        print("This is the original CSV file, in a dataframe format \n", df_target)
        col = df_target.columns #Columns are made up of 2 strings that are ineffecient
        new_cols = refactor_columns(col)
        print("Creating new file")

        df_target = format_df_target(df_target)
        new_df = pd.DataFrame(columns=["name", "tag", "origin"])
        #need to put in argument for new_columns checker, could assign numbers and change after
        start = time.time()
        for i in range(len(df_target)):
            print("Testing second iterration")
            text_arg = df_target.loc[i, "text"].split(",")
            text_arg[-1] = "0"
            text_temp = text_arg[2:]
            for p in range(len(text_temp)):
                if text_temp[p] != "0":
                    origins = new_cols[p+2] #The +2 Counteracts the slice action
                    print(text_arg, origins, "\n", new_cols)
                    print("Testing aspects:", len(text_arg), len(new_cols))
                    new_df = new_df.append({"name": text_arg[0], "tag": text_arg[1], "origin": origins}, ignore_index=True)
                    #By placing the DF assignment here the file should create multiple versions of the same name with individual origins assigned to them, which will speed up later search functions
                    print(p)

            #Although inline text version is quicker, there are issues with duplicate values origins = [new_cols[text_arg.index(b)] for b in text_arg[2:] if b != "0"]
            #This should eliminate any duplicate values inside of the list
        end = time.time()
        print(new_df, pd.unique(new_df["tag"]))
        make_cross_compatible(new_df)
        print("Time elapsed: ", start - end)
        print(pd.unique(new_df["tag"]))
        new_df.to_excel("firstnames_cleaned.xlsx", index=False)
        return new_df

def make_cross_compatible(new_df):
    new_df["name"] = new_df["name"].str.replace("+", "-")
    new_df["tag"] = new_df["tag"].str.replace("1F", "WF").replace("?F", "WF")  # Weighted Female - most likely to be female
    new_df["tag"] = new_df["tag"].str.replace("1M", "?M").replace("?M", "WM")  # Weighted Male - most likely to be male
    new_df["tag"] = new_df["tag"].str.replace("?", "NN")  # name is neutral, non last name



def check_if_exists():
    outcome = False
    if os.path.exists("firstnames_cleaned.xlsx"):
        test_df = pd.read_excel("firstnames_cleaned.xlsx")
        sample = test_df.sample(20)
        print(sample)
        #print(test_df[50:80], test_df[4000:4001])
        case1, case2, case3, case4 = test_df.iloc[60], test_df.iloc[70], test_df.iloc[80], test_df.iloc[4000]
        print(case1["name"], case2["name"], case3["name"], case4["name"])
        if case1["name"] == "Aart" and case2["name"] == "Aatu" \
                and case3["name"] == "Abaz" and case4["name"] == "Annamarie":
            print("The cleaned file is valid")
            outcome = True

    return outcome


def format_df_target(df_target):
    a, b = df_target.columns[0], df_target.columns[1]
    df_target = df_target.rename(columns={a: "text", b: "na"})
    df_target["text"] = df_target["text"].str.replace(";;", ",0,0") #Crude fix, bad data to blame
    df_target["text"] = df_target["text"].str.replace(";", ",")
    df_target["text"] = df_target["text"].str.replace(",,", ",")
    df_target = df_target.drop(columns=["na"])
    return df_target


def refactor_columns(col):
    new_columns = []
    for i in range(len(col)):
        line = col[i]
        out = line.split(";")
        new_columns = new_columns + out
    nations = new_columns

    nations[4], nations[12], nations[26] = "USA", "Dutch", "Czech"
    nations.pop(-1)
    print(nations)
    nations.remove("etc.")
    return nations

def form_internationa_name_dict():
    #This function uses wikipedia and wiktionaries catagory tags, as the layout is standardised in both
    #Wikipedia: https://en.wikipedia.org/wiki/Category:Given_names_by_culture - Wiktionary: https://en.wiktionary.org/w/index.php?title=Category:Given_names_by_language&subcatuntil=Tongan%0ATongan+given+names#mw-subcategories
    print("Generating international names")


def form_latin_name_dict():
    test_case = False
    test_decision = True
    name_dict = {}
    nations = ["French", "Italian", "Spanish", "Turkish", "Dutch", "Swedish", "Polish", "Serbian", "Irish",
                       "Czech", "Hungarian", "Russian", "Persian", "Basque", "Armenian", "German"] #Test cases to see if wiktionary will take these as a real argument
    nation_abrev = ["France", "Italy", "Spain", "Turkey", "Dutch", "Sweden", "Poland", "Serbia", "Ireland",
                            "Czech", "Hungary", "Russia", "Arabia/Persia", "Basque", "Armenia", "German"]
    probable_formats = ["dd", "dd", "dd", "dd", "li", "dd", "td", "li", "li", "dd", "dd", "td", "li", "dd",
                        "li", "dd"]
    name_div = ["Abbée", "Abbondanza" "Abdianabel", "Abay", "Aafke", "Aagot",  "Adela", "Anica",
                        "Aengus", "Ada", "Adél", "Авдотья", "Aban", "Abarrane", "Akabi", "Aaltje"]
    name_fin = ["Zoëlle", "Zelmira", "Zulema", "Zekiye", "Zjarritjen", "Öllegård", "Żywia",
                "Vida", "Nóra", "Zorka", "Zseraldin", "Ярослава", "Yasmin", "Zuriňe", "Zoulal", "Zwaantje"]
    if os.path.exists("npcs.csv") or os.path.exists("npcs.xlsx"):
        print("File already exists")
        try:
            #print("We're getting there")
            df_csv, df_xlsx= pd.read_csv("npcs.csv"), pd.read_excel("npcs.xlsx")
            file_list = [df_csv, df_xlsx]
            #print("Starting the soup is recommended before taking the test\nIf you wish to skip this step please ensure that everything is working in order...")

            test_result = start_tests(file_list, nation_abrev)
            print("Test result: ", test_result)

            #If you decide you need to add new names, please ensure you have added the following things
            #1. The nations name, relative to the wikipedia article, for instance https://en.wiktionary.org/wiki/Appendix:Russian_given_names
            #2. The nations abreviation, eg ENG for english
            #3. The format of the HTML that is being used to hold the names
            #4. The first female name to change the gender type from male to female
            #5. The last name needed, as an end point (As wikipedia often adds extra things to the end of a file using
            #The HTML type that is being read by BS4)
            test_case = start_soup(test_case)
            #form_non_latin(file_list)
            df_csv = clean_df(df_csv)
            df_stable = translit_non_latin(df_csv)

            if test_case == True:
                #Move function here
                print("Starting up Beautiful Soup")

                df = pd.DataFrame(columns=["name", "tag", "origin"])
                df = add_names(df, name_div, name_fin, nation_abrev, nations, probable_formats)
                df = translit_non_latin(df)
                form_files(df)
                print(df.tail(60))

                return df
            else:
                return df_stable
        except:
            print("An error occured")
            pass
    else:
        print("File does not exist, starting up Beautiful Soup and creating files")
        df = pd.DataFrame(columns=["name", "tag", "origin"])
        df = add_names(df, name_div, name_fin, nation_abrev, nations, probable_formats)
        df = translit_non_latin(df)
        form_files(df)
        print(df.tail(60))

        return df


def start_soup(add_decision):
    input_finish = False
    while not input_finish:
        print("add new names: [y/n?]")

        answer = input("\n\n\n")
        if answer.lower() == "y" or answer.lower() == "yes":
            print("Adding new files")
            add_decision = True
            input_finish = True
        elif answer.lower() == "n" or answer.lower() == "no":
            print("Returing Dataframe")
            add_decision = False
            input_finish = True
        else:
            print("That is an invalid input, please type either Y or N")
    return add_decision


def add_names(df, name_div, name_fin, nation_abrev, nations, probable_formats):
    for i in range(len(nations)):
        divide = False
        argument = "https://en.wiktionary.org/wiki/Appendix:{}_given_names".format(nations[i])
        file = requests.get(argument)
        print(str(file), "Iteration is {}".format(i), nations[i])
        if str(file) == "<Response [404]>":
            pass
        elif str(file) == "<Response [200]>":
            soup = BeautifulSoup(file.content, "html.parser")
            rec_data = soup.find_all(probable_formats[i])
            item_txt = ""
            for item in rec_data:
                item_txt = item.string
                origins = nation_abrev[i]
                if item_txt is None:
                    #print(item.text)
                    item_split = item.text.split(" ")
                    item_txt = item_split[0]
                    item_txt = re.sub( r"([A-Z])", r" \1", item_txt).split()
                    item_txt = item_txt[0]
                    item_txt = item_txt.strip()
                print(item.string)
                print("Divided text: ", item_txt)
                if item_txt == name_div[i - 1]:  # First female entry
                    divide = True
                if item_txt == name_fin[i]:  # Last acceptable entry
                    adder = str(item_txt)

                    df = df.append({"name": adder, "tag": "F", "origin": origins},
                                   ignore_index=True)
                    break

                if item_txt is not None:
                    adder = str(item_txt)
                    parts = re.split(r'[;,\s]\s*', adder)  # removes any double names that are not hyphinated
                    print(parts)
                    adder = parts[0]
                    if not adder.strip():
                        print("Not Found")
                        pass
                    print(adder)
                    if adder == name_div[-1]:
                        # Had to add this to fix the polish names set, should rework later
                        divide = True
                    if not divide:
                        df = df.append({"name": adder, "tag": "M", "origin": origins},
                                       ignore_index=True)
                    else:
                        df = df.append({"name": adder, "tag": "F", "origin": origins},
                                       ignore_index=True)
    df = clean_df(df)
    return df


def clean_df(df):
    df["name"] = df["name"].str.replace("[^\w\s]", "")
    df["name"] = df["name"].str.replace("[\b\d+(?:\.\d+)?\s+]", "")
    df = df.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)
    df = df.drop_duplicates(subset="name", keep="first")
    return df


def start_tests(file_in, nation):
    print("Starting test case ...\nUsing the following values", file_in, nation)
    nation_abrev = nation
    correct_responses = []
    for i in range(len(file_in)): #Goes through both files (csv and excel)
        df_arg = file_in[i] #Created dataframe
        for i in range(len(nation_abrev)): #Goes through each nationality present

            #print(i) Test
            df_temp = df_arg.loc[df_arg["origin"] == nation_abrev[i]] #Loads temp dataframe filled with nationality
            if df_temp.size > 99: #If the temp file is bigger than 10, assume the DF is correctly loaded
                print("Size of names relating to : {} is adequate".format(nation_abrev[i]))
                correct_responses.append(i) #adds to list
            else:
                print("Origin is missing names, would recommend adding files")
                return False

    if len(correct_responses) == len(nation_abrev) * 2:
        print("Tests appear to be fine, you can skip the BS4 implementation")
        return True
    else:
        return False

def translit_non_latin(df):
    #This function will first add names that are in non latin cases, eg. russian names and
    #Will translate them along with any other names that already exist in the DF
    non_latin_languages = ["Russia", "Serbia"]
    print("*\n*\n*\n*\n*\n")
    for column in df.columns:
        df_copy = df.loc[(df["origin"] == "Serbia") | (df["origin"] == "Russia")] #Add any other languages that may use Cyrillic Script
        for index, row in df_copy.iterrows():
            name = row[0]
            language_code = detect_language(name)
            if language_code is not None:
                print("Translating ...")
                print(language_code)
                print(row)
                print(translit(name, "{}".format(language_code), reversed=True))
                latin_name = translit(name, "{}".format(language_code), reversed=True)
                df.at[index, "name"] = latin_name
    print(df)
    return df

def generate_city_input():
    #Function will use DCGAN with geonames to create plausible settlement / city names along side NPC generator
    #https://www.geonames.org/
    print("This function has not been implemented yet")

def form_files(data):
    #Aims to create a CSV, Excell and SQL version of the dataframe
    data.to_csv("npcs.csv", index=False)
    data.to_excel("npcs.xlsx", index=False)
    #Continue Later
    #data.to_sql()




#df = form_latin_name_dict()
#df = splice_names()
#print(df)
soup_surnames()


