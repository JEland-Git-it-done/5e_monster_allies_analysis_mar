import pandas as pd; import numpy as np;
import requests; import os; import re
from bs4 import BeautifulSoup
from transliterate import translit, detect_language



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

npc_df = None

def npc_scandi_male():
    df = pd.read_excel("boys_NW_NPC.xlsx")
    df = df.rename(columns={"Historical top boys' names. 1880-2019" : "year"})
    for i in range(10):
        df = df.rename(columns={"Historical top boys' names. 1880-2019.{}".format(str(i + 1)) : str(i + 1)})
    df = df.dropna(axis="index")
    for x in range(len(df.columns) - 1):
        x += 1
        df["{}".format(str(x))] = [y.replace("\*","") for y in df["{}".format(str(x))]]

    print(df.columns)
    print(df)

def german_names(): #This function is a test case of reading a wikipedia list to source names, with the names being loaded in DL elements (descriptive lists)
    #letters = list(string.ascii_uppercase)#
    if os.path.exists("npcs.csv"):
        df = pd.read_csv("npcs.csv")
        df = df[df["origin"] == "GER"]
        print(df)
        return df
    else:

        df = pd.DataFrame(columns=["name","tag", "origin"])

        file = requests.get("https://en.wiktionary.org/wiki/Appendix:German_given_names")
        soup = BeautifulSoup(file.content, "html.parser")
        rec_data = soup.find_all("dd")
        name_divided = False
        for item in rec_data:
            if item.string == "Aaltje":
                name_divided = True
            if item.string is not None:
                adder = str(item.string)
                if not name_divided:
                    df = df.append({"name":adder, "tag":"M", "origin":"GER"}, ignore_index=True)
                elif name_divided:
                    df = df.append({"name":adder, "tag":"F", "origin":"GER"}, ignore_index=True)
                    pass
    df = german_surnames(df)

    df_no_non = df.fillna(0)

    print(df_no_non)
    #df_no_non = df_no_non.drop_duplicates(subset="name", keep=False, inplace=True)
    df_complete = df_no_non[df_no_non.values != 0]

    print(df_complete)
    return df_complete

def german_surnames(dataframe):
    file = requests.get("https://en.wiktionary.org/wiki/Appendix:German_surnames")
    soup = BeautifulSoup(file.content, "html.parser")
    rec_data = soup.find_all("li")
    for item in rec_data:
        if item.string == "German family name etymology":#This is the final part of the page, is used to exit loop
            break
        if item.string is not None:
            adder = str(item.string)
            if "(disambiguation)" in adder:
                adder.replace("(disambiguation)", "")
            print(adder)
            dataframe = dataframe.append({"name": adder, "tag":"S", "origin":"GER"}, ignore_index=True) #S tag is indicative of the surname
    dataframe["name"] = dataframe["name"].str.replace("[^\w\s]", "")
    print(dataframe.tail(10))
    return dataframe

def italian_names():
    file = requests.get("https://en.wiktionary.org/wiki/Appendix:Italian_given_names")
    soup = BeautifulSoup(file.content, "html.parser")
    rec_data = soup.find_all("dd")
    name_div = False
    df = pd.DataFrame(columns=["name", "tag", "origin"])
    for item in rec_data:
        if item.string == "Abbondanza":#First female entry
            name_div = True
        if item.string == "Zelmira":#Final part of page, exits loop
            df = df.append({"name": adder, "tag": "F", "origin": "ITA"}, ignore_index=True)
            break
        if item.string is not None:
            adder = str(item.string)
            if not name_div:
                df = df.append({"name": adder, "tag":"M", "origin":"ITA"}, ignore_index=True)
            else:
                df = df.append({"name": adder, "tag":"F", "origin": "ITA"}, ignore_index=True)
    df["name"] = df["name"].str.replace("[^\w\s]", "")
    print(df)
    return df

def italian_surnames():
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



def form_name_dict():
    test_case = False
    test_decision = True
    name_dict = {}
    nations = ["French", "Italian", "Spanish", "Turkish", "Dutch", "Swedish", "Polish", "Serbian", "Irish",
                       "Czech", "Hungarian", "Russian"] #Test cases to see if wiktionary will take these as a real argument
    nation_abrev = ["FRA", "ITA", "SPA", "TUR", "DUT", "SWE", "POL", "SRB", "IRE",
                            "CZE", "HUN", "RUS"]
    probable_formats = ["dd", "dd", "dd", "dd", "li", "dd", "td", "li", "li", "dd", "dd", "td"]
    name_div = ["Abbée", "Abbondanza" "Abdianabel", "Abay", "Aafke", "Aagot",  "Adela", "Anica",
                        "Aengus", "Ada", "Adél", "Авдотья"]
    name_fin = ["Zoëlle", "Zelmira", "Zulema", "Zekiye", "Zjarritjen", "Öllegård", "Żywia",
                        "Vida", "Nóra", "Zorka", "Zseraldin", "Ярослава"]
    if os.path.exists("npcs.csv") or os.path.exists("npcs.xlsx"):
        print("File already exists")
        try:
            df_csv, df_xlsx= pd.read_csv("npcs.csv"), pd.read_excel("npcs.xlsx")
            file_list = [df_csv, df_xlsx]
            test_case = start_tests(file_list, nation_abrev)

            #form_non_latin(file_list)
            print("Test result: ", test_case)
            print(test_case)
            test_case = start_soup(test_case)
            df_stable = form_non_latin(df_csv)

            #If you decide you need to add new names, please ensure you have added the following things
            #1. The nations name, relative to the wikipedia article, for instance https://en.wiktionary.org/wiki/Appendix:Russian_given_names
            #2. The nations abreviation, eg ENG for english
            #3. The format of the HTML that is being used to hold the names
            #4. The first female name to change the gender type from male to female
            #5. The last name needed, as an end point (As wikipedia often adds extra things to the end of a file using
            #The HTML type that is being read by BS4)
            if test_case == False:
                #Move function here
                print("Starting up Beautiful Soup")

                df = pd.DataFrame(columns=["name", "tag", "origin"])
                df = add_names(df, name_div, name_fin, nation_abrev, nations, probable_formats)
                form_files(df)
                print(df.tail(60))

                return df
            else:
                return df_stable
        except:
            pass
    else:
        print("File does not exist, starting up Beautiful Soup and creating files")
        df = pd.DataFrame(columns=["name", "tag", "origin"])
        df = add_names(df, name_div, name_fin, nation_abrev, nations, probable_formats)
        form_files(df)
        print(df.tail(60))

        return df


def start_soup(add_decision):
    input_finish = False
    while not input_finish:
        print("Do you need to add new names? [y/n?]")

        answer = input("\n\n\n")
        if answer.lower() == "y":
            print("Adding new files")
            add_decision = False
            input_finish = True
        elif answer.lower() == "n":
            print("Returing Dataframe")
            add_decision = True
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
            for item in rec_data:
                print(item.string)
                if item.string == name_div[i - 1]:  # First female entry
                    divide = True
                if item.string == name_fin[i]:  # Last acceptable entry
                    adder = str(item.string)
                    df = df.append({"name": adder, "tag": "F", "origin": "{}".format(nation_abrev[i])},
                                   ignore_index=True)
                    break
                if item.string is not None:
                    adder = str(item.string)
                    parts = re.split(r'[;,\s]\s*', adder)  # removes any double names that are not hyphinated
                    adder = parts[0]
                    if not adder.strip():
                        print("Not Found")
                        pass
                    print(adder)
                    if adder == name_div[-1]:
                        # Had to add this to fix the polish names set, should rework later
                        divide = True
                    if not divide:
                        df = df.append({"name": adder, "tag": "M", "origin": "{}".format(nation_abrev[i])},
                                       ignore_index=True)
                    else:
                        df = df.append({"name": adder, "tag": "F", "origin": "{}".format(nation_abrev[i])},
                                       ignore_index=True)
    df["name"] = df["name"].str.replace("[^\w\s]", "")
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
            df_temp = df_arg.loc[df_arg["origin"] == "{}".format(nation_abrev[i])] #Loads temp dataframe filled with nationality
            print(df_temp)
            if df_temp.size > 99: #If the temp file is bigger than 10, assume the DF is correctly loaded
                print("Size is adequate")
                correct_responses.append(i) #adds to list

    if len(correct_responses) == len(nation_abrev) * 2:
        print("Tests appear to be fine, can skip the BS4 implementation")
        return True
    else:
        return False

def form_non_latin(df):
    #This function will first add names that are in non latin cases, eg. russian names and
    #Will translate them along with any other names that already exist in the DF
    non_latin_languages = ["RUS", "SRB"]
    print("*\n*\n*\n*\n*\n")
    for column in df.columns:
        df_copy = df.loc[(df["origin"] == "SRB") | (df["origin"] == "RUS")]
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



def form_files(data):
    #Aims to create a CSV, Excell and SQL version of the dataframe
    data.to_csv("npcs.csv", index=False)
    data.to_excel("npcs.xlsx", index=False)
    #Continue Later
    #data.to_sql()

def form_npc_csv():
    #There is a strong argument to make this into an SQL file aswell, but for now CSV will do
    available_df = {1:german_names(), 2:german_surnames(german_names())}
    df_copy = german_names()
    df_copy.drop_duplicates(["name"], keep="last")


    print(df_copy)
    df_copy.to_csv("npcs.csv", index=False)
    #DF outputs duplicated even though duplicates are dropped above, needs to be fixed


df = form_name_dict()
print(df)