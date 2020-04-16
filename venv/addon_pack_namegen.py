import pandas as pd; import numpy as np;
import requests; import os; import re; import json
from bs4 import BeautifulSoup
from transliterate import translit, detect_language; import time



#This addon pack focuses on the application of current and historic data to create more organic naming conventions for NPC's
#The following dataset will act as an anchor for this https://www.ssb.no/en/navn#renderAjaxBanner
#https://www.europeandataportal.eu/data/datasets?locale=en&tags=vornamen&keywords=vornamen
#Changed idea to read wikipedia pages eg. https://en.wikipedia.org/w/index.php?title=Category:German-language_surnames&pagefrom=Eschenbach%0AEschenbach+%28surname%29#mw-pages
#https://archaeologydataservice.ac.uk/archives/view/atlas_ahrb_2005/datasets.cfm?CFID=331341&CFTOKEN=70517262
#Any information taken from https://www.europeandataportal.eu is being used under the Creative Commons Share-Alike Attribution Licence (CC-BY-SA), none is currently being used.
#Arcane name set seems like a useful idea, see text below
#Look into GeoNames dataset found here, https://github.com/awesomedata/awesome-public-datasets , could be used for expanded town name generator
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
def read_surnames():
    #https://en.wiktionary.org/wiki/Category:Surnames_by_language
    #This function aims to go through each of the catagories listed in the above link, goes through each entry and tries to assign them to one of the pre existing lists
    print("Attempting to webscrape surnames, along with some straggeler forenames")

def splice_names():
    #Please note that most of the names involved in this function are infact latin-ised names, and cover countries that have already been found via web scraping
    df = form_international_names()
    df_bs4 = form_latin_name_dict()
    test_df = df_bs4.loc[df_bs4["origin"] == "IRA"]
    print(pd.unique(test_df["name"]))
    frames = [df, df_bs4]
    #standardize_files(frames)
    df_merge = pd.concat(frames)
    print(df_merge)
    #mutable_list = pd.unique(df_merge["origin"])
    #print(mutable_list)
    #Implements standardization between the two tables
    return df_merge


def form_international_names(): #add npc_df as argument
    #Due to a distinct lack of international names, outside of europe from the previous sources
    #This function will use the first name database provided by Matthias Winkelmann and Jörg MICHAEL at the following adress
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
            origins = []
            text_arg = df_target.loc[i, "text"].split(",")
            text_arg[-1] = "0"
            text_temp = text_arg[2:]
            for p in range(len(text_temp)):
                if text_temp[p] != "0":
                    origins.append(new_cols[p+2]) #The +2 Counteracts the slice action
                    print(p)

            #Although inline text version is quicker, there are issues with duplicate values origins = [new_cols[text_arg.index(b)] for b in text_arg[2:] if b != "0"]
            #This should eliminate any duplicate values inside of the list
            print(text_arg, origins, "\n", new_cols)
            print("Testing aspects:", len(text_arg), len(new_cols))
            new_df = new_df.append({"name": text_arg[0], "tag": text_arg[1], "origin": origins}, ignore_index=True)

        end = time.time()
        print(new_df, pd.unique(new_df["tag"]))
        make_cross_compatible(new_df)


        print("Time elapsed: ", start - end)

        print(pd.unique(new_df["tag"]))
        new_df.to_excel("firstnames_cleaned.xlsx", index=False)

        return new_df


def make_cross_compatible(new_df):
    new_df["name"] = new_df["name"].str.replace("+", "-")
    new_df["tag"] = new_df["tag"].str.replace("1F", "WF").replace("?F",
                                                                  "WF")  # Weighted Female - most likely to be female
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
        #print(case1["name"], case2["name"], case3["name"])
        if case1["name"] == "Abay" and case2["name"] == "Abbondanzio" \
                and case3["name"] == "Abdel-Fattah" and case4["name"] == "Bao-Lian":
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
            df_csv, df_xlsx= pd.read_csv("npcs.csv"), pd.read_excel("npcs.xlsx")
            file_list = [df_csv, df_xlsx]
            test_case = start_tests(file_list, nation_abrev)

            #form_non_latin(file_list)
            print("Test result: ", test_case)
            df_csv = clean_df(df_csv)
            test_case = start_soup(test_case)
            df_stable = translit_non_latin(df_csv)


            #If you decide you need to add new names, please ensure you have added the following things
            #1. The nations name, relative to the wikipedia article, for instance https://en.wiktionary.org/wiki/Appendix:Russian_given_names
            #2. The nations abreviation, eg ENG for english
            #3. The format of the HTML that is being used to hold the names
            #4. The first female name to change the gender type from male to female
            #5. The last name needed, as an end point (As wikipedia often adds extra things to the end of a file using
            #The HTML type that is being read by BS4)
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
                origins = []
                item_txt = item.string
                origins.append(nation_abrev[i])
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
    print("Starting test case ...")
    nation_abrev = nation
    correct_responses = []
    for i in range(len(file_in)): #Goes through both files (csv and excel)
        df_arg = file_in[i] #Created dataframe
        for i in range(len(nation_abrev)): #Goes through each nationality present

            #print(i) Test
            df_temp = df_arg.loc[df_arg["origin"]] #Loads temp dataframe filled with nationality
            print(df_temp)
            if df_temp.size > 99: #If the temp file is bigger than 10, assume the DF is correctly loaded
                print("Size is adequate")
                correct_responses.append(i) #adds to list
            else:
                print("Origin is missing names, would recommend adding files")
                return False

    if len(correct_responses) == len(nation_abrev) * 2:
        print("Tests appear to be fine, can skip the BS4 implementation")
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
df = splice_names()

print(df)
