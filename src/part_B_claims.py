# ----------------Extract claims from patent docs-----------------
# --------------------- IR Assignment ----------------------------
# -------------------------- IHU ---------------------------------
# ---------------------- 2020 - 2021 -----------------------------
# ---- [Giorgos Kyros - [112020], Manolas Ioannis - [132020]] ----
# ----------------------------------------------------------------

# ----------------Libraries----------------

import numpy as np
import pandas as pd
import os
from bs4 import BeautifulSoup
import glob
import re
from lxml import etree

# ----------------Initialize variables----------------
number_of_docs = 0
ipc_count = 0
countries = []
titles = 0
ipcs = 0
classes = 0
abstracts = 0
descriptions = 0
claims = 0
all_previous = 0
abs_and_claims = 0
desc_and_claims = 0
abs_and_desc = 0
en_main = 0
res = []
ids = []

# -----------Function to check duplicates entries in list-----------

def has_duplicates(iterable):
    seen = []
    for x in iterable:
        if x in seen:
            return True
    return False

# -----------Function to check and return onlyNumeric elements from string-----------

def only_numerics(seq):
    seq_type = type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))

# -----------Preprocessing claims_text, get only 1 space between characters and remove some noise strings-----------

def clean_claims(a):
    a = a.replace(" CLAIMS1. ", "")
    a = a.replace("Claims:1. ", "")
    a = a.replace("CLAIMS1. ", "")
    a = a.replace("CLAIMS:1. ", "")
    a = a.replace("Claimed", "")
    a = a.replace("claimed", "")
    a=re.sub(' +', ' ', a)
    return a

c = 0

# ----------- List to append patend-id for each case -----------
case1 = []
case2 = []
case3 = []
case4 = []

# -----------Dictionary -----------

words = {"word":["claims", "claim", "Claim","Claims", "CLAIM", "CLAIMS", "Ansprüche", "Ansprüchen", "Anspruch","ansprüche" , "anspruch","revendication" , "revendications", "Revendication" , "Revendications"]}
# Path of the main folder of patent files.
dir = 'patents/'

# Read all the files from directories and subdirectories with walk.

for subdir, dirs, files in os.walk(dir):
    for file in files:
        filepath = os.path.join(subdir, file)
        soup = BeautifulSoup(open(filepath, encoding="utf8"), 'xml')
        number_of_docs += 1
        ids = soup.find_all('patent-document')
        claims = soup.find_all('claims')
        print(number_of_docs)

        # Procedure to seperate claims and find depedent, indepedent and build union claims
        # There are 3 cases
        # @Case1 -> Correct Classify with num section
        # @Case2 -> Correct Classify with claim-text
        # @Case3 -> Wrong Classify with claim-text

        if claims:          
            print(file)
            counter_cl = 1
            depedent = []
            union = []
            indepedent = []
            claims_arr = []
            c += 1

            for claim in claims:
                counter_c = 1
                # Open file claims_res.txt to write the results of algorithm
                with open('claims1.txt', 'a+', encoding='utf-8') as writer:
                    # @Case1 -> Has all correct nums
                    if claim.find("claim").get("num"):
                        if len(claim.find_all("claim")) > 1 and int(claim.find("claim")["num"])>0:
                            # write trek tags suchs as [DOCNO, CLAIMS, etc]
                            writer.write("<DOCNO>\n")
                            writer.write(str(ids[0]["ucid"]) + "\n")
                            
                            # append doc-ucid for each case
                            case1.append(ids[0]["ucid"])
                            writer.write("</DOCNO>\n")
                            writer.write("<CLAIMS>\n")
                            data = {}
                            for a in claim.find_all("claim"):
                                # append claim.text in <claim num=#> tag
                                a = clean_claims(a.text)
                                claims_arr.append(a)
                                # write claim each time
                                writer.write("<CLAIM" + str(counter_c) + ">\n")
                                writer.write(str(a) + "\n")
                                writer.write("</CLAIM" + str(counter_c) + ">\n")

                                # Procedure to find depedent and indepedent claims in all languages [EN, DE, FR] and union claims
                                # with regex word-key [in dict words{}]
                                for word in words["word"]:
                                    if re.search(word + " [0-9]", a):
                                        depedent.append(counter_c)
                                        if (only_numerics(a[a.find(word) + len(word):a.find(word) + len(word) + 3])):
                                            v = int(only_numerics(a[a.find(word) + len(word):a.find(word) + len(word) + 3]))
                                        if v in data:
                                            data[v].append(a[a.find(word) + len(word) + 4:len(a)])
                                            # data_numbers[v].append(counter_c)
                                        else:
                                            if v<=len(claims_arr):
                                                data[v] = [claims_arr[v-1]]
                                                data[v].append(a[a.find(word) + len(word) + 4:len(a)])
                                
                                # Compute depedenet and indepedent claims based on previous procedure
                                if counter_c not in depedent:
                                    if counter_c not in indepedent:
                                       indepedent.append(counter_c)
                                counter_c += 1

                            # Write close tags and extra depedent, indepedent and union tags    
                            writer.write("</CLAIMS>\n")
                            writer.write("<INDEPEDENT>\n")
                            writer.write(str(indepedent) + "\n")
                            writer.write("</INDEPEDENT>\n")
                            writer.write("<DEPEDENT>\n")
                            writer.write(str(depedent) + "\n")
                            writer.write("</DEPEDENT>\n")

                            # Write union tags
                            writer.write("<UNION> \n")
                            for t in data:
                                writer.write("\nUNION CLAIM "+str(t) + " :\n" + ', '.join(data[t]) + "\n")
                            writer.write("</UNION>\n")
                        else:
                            # @Case2 -> Has one <claim num=#>, but has <claim-text>
                            writer.write("<DOCNO>\n")

                            # append doc-ucid for each case
                            case2.append(ids[0]["ucid"])
                            writer.write(str(ids[0]["ucid"]) + "\n")
                            writer.write("</DOCNO>\n")
                            writer.write("<CLAIMS>\n")
                            claims_n1 = []
                            claims_arr= []
                            counter_dep = 1
                            data = {}

                            # append claim.text in <claim num=#> tag
                            for cl in claim.find_all("claim-text"):
                                
                                # append claim.text in <claim-text> tag after of preprocessing
                                a = clean_claims(cl.text)

                                # Check if claim text starts with number so save it as distinct claim 
                                if (only_numerics(a[0:25]).isnumeric() and counter_c == 1) or only_numerics(
                                        a[0:10]).isnumeric():
                                    a = a.strip()
                                    # We detected some cases that claim there is in another claim-text, 
                                    # so below from this we search and find and make a new claim
                                    if claims_n1 and re.search(" [0-9]?[0-9]?[0-9]\. ", a[31:len(a) - 2]):
                                        writer.write("<CLAIM" + str(counter_c) + ">\n")
                                        for text in claims_n1:
                                            writer.write(str(text).strip() + "\n")
                                        writer.write("</CLAIM" + str(counter_c) + ">\n")
                                        counter_c += 1
                                        claims_n1 = []
                                        claims_arr.append(str(re.split(" [0-9]?[0-9]?[0-9]\. ", a)[0]))
                                        claims_n1.append(str(re.split(" [0-9]?[0-9]?[0-9]\. ", a)[0]))
                                        writer.write("<CLAIM" + str(counter_c) + ">\n")
                                        writer.write(str(claims_n1[0]).strip() + "\n")
                                        writer.write("</CLAIM" + str(counter_c) + ">\n")
                                        claims_n1 = []
                                        counter_c += 1
                                        claims_arr.append(str(counter_c) + ". " + str(re.split(" [0-9]?[0-9]?[0-9]\. ", a)[1]))
                                        claims_n1.append(str(counter_c) + ". " + str(re.split(" [0-9]?[0-9]?[0-9]\. ", a)[1]))
                                        continue
                                    elif claims_n1:
                                        writer.write("<CLAIM" + str(counter_c) + ">\n")
                                        for text in claims_n1:
                                            writer.write(str(text).strip() + "\n")
                                        writer.write("</CLAIM" + str(counter_c) + ">\n")
                                        counter_c += 1
                                    claims_n1 = []
                                    claims_arr.append(a)
                                    claims_n1.append(a)
                                else:
                                    if counter_c == 1:
                                        continue
                                    else:
                                        z = claims_arr[-1]
                                        del claims_arr[-1]
                                        claims_arr.append(z+a)
                                        claims_n1.append(a)

                            # Procedure to find depedent and indepedent claims in all languages [EN, DE, FR] and union claims
                            # with regex word-key [in dict words{}]
                            for claims_arra in claims_arr:
                                for word in words["word"]:
                                    if re.search(word + " [0-9]", claims_arra):
                                        depedent.append(counter_dep)
                                        if (only_numerics(claims_arra[claims_arra.find(word) + len(word):claims_arra.find(word) + len(word) + 3])):
                                            v = int(only_numerics(claims_arra[claims_arra.find(word) + len(word):claims_arra.find(word) + len(word) + 3]))
                                        if v in data:
                                            data[v].append(claims_arra[claims_arra.find(word) + len(word) + 4:len(claims_arra)-2])
                                            # data_numbers[v].append(counter_c)
                                        else:
                                            if v <= len(claims_arr):
                                                data[v] = [claims_arr[v - 1]]
                                                data[v].append(claims_arra[claims_arra.find(word) + len(word) + 4:len(claims_arra)])
                                
                                # Compute depedenet and indepedent claims based on previous procedure
                                if counter_dep not in depedent:
                                    if counter_dep not in indepedent:
                                        indepedent.append(counter_dep)
                                counter_dep+=1
                            
                            # Write close tags and extra depedent, indepedent and union tags
                            writer.write("<CLAIM" + str(counter_c) + ">\n")
                            for text in claims_n1:
                                writer.write(str(text).strip() + "\n")
                            writer.write("</CLAIM" + str(counter_c) + ">\n")
                            writer.write("</CLAIMS>\n")
                            writer.write("<INDEPEDENT>\n")
                            writer.write(str(indepedent) + "\n")
                            writer.write("</INDEPEDENT>\n")
                            writer.write("<DEPEDENT>\n")
                            writer.write(str(depedent) + "\n")
                            writer.write("</DEPEDENT>\n")

                            # Write union tags
                            writer.write("<UNION> \n")
                            for t in data:
                                writer.write("\nUNION CLAIM " + str(t) + " :\n" + ', '.join(data[t]) + "\n")
                            writer.write("</UNION>\n")
                    else:
                        if claim.find_all("claim-text"):

                            # @Case3 -> Has not <claim num=#>, but has <claim-text>, or has <claim-text> in wrong format
                            writer.write("<DOCNO>\n")
                            
                            # append doc-ucid for each case
                            case3.append(ids[0]["ucid"])
                            writer.write(str(ids[0]["ucid"]) + "\n")
                            writer.write("</DOCNO>\n")
                            writer.write("<CLAIMS>\n")
                            claims_n1 = []
                            claims_arr = []
                            counter_dep = 1
                            data = {}

                            # Append claim.text in <claim-text> tag
                            for cl in claim.find_all("claim-text"):

                                # append claim.text in <claim-text> tag after of preprocessing
                                a = clean_claims(cl.text)

                                # Check if claim text starts with number so save it as distinct claim
                                if (only_numerics(a[0:25]).isnumeric() and counter_c == 1) or only_numerics(
                                        a[0:10]).isnumeric():
                                    a = a.strip()
                                    
                                    # We detected some cases that claim there is in another claim-text, 
                                    # so below from this we search and find and make a new claim
                                    if claims_n1 and re.search(" [0-9]?[0-9]?[0-9]\. ", a[31:len(a) - 2]):
                                        writer.write("<CLAIM" + str(counter_c) + ">\n")
                                        for text in claims_n1:
                                            writer.write(str(text).strip() + "\n")
                                        writer.write("</CLAIM" + str(counter_c) + ">\n")
                                        counter_c += 1
                                        claims_n1 = []
                                        claims_arr.append(str(re.split(" [0-9]?[0-9]?[0-9]\. ", a)[0]))
                                        claims_n1.append(str(re.split(" [0-9]?[0-9]?[0-9]\. ", a)[0]))
                                        writer.write("<CLAIM" + str(counter_c) + ">\n")
                                        writer.write(str(claims_n1[0]).strip() + "\n")
                                        writer.write("</CLAIM" + str(counter_c) + ">\n")
                                        claims_n1 = []
                                        counter_c += 1
                                        claims_arr.append(
                                            str(counter_c) + ". " + str(re.split(" [0-9]?[0-9]?[0-9]\. ", a)[1]))
                                        claims_n1.append(
                                            str(counter_c) + ". " + str(re.split(" [0-9]?[0-9]?[0-9]\. ", a)[1]))
                                        continue
                                    elif claims_n1:
                                        writer.write("<CLAIM" + str(counter_c) + ">\n")
                                        for text in claims_n1:
                                            writer.write(str(text).strip() + "\n")
                                        writer.write("</CLAIM" + str(counter_c) + ">\n")
                                        counter_c += 1
                                    claims_n1 = []
                                    claims_arr.append(a)
                                    claims_n1.append(a)
                                else:
                                    if counter_c == 1:
                                        continue
                                    else:
                                        z = claims_arr[-1]
                                        del claims_arr[-1]
                                        claims_arr.append(z + a)
                                        claims_n1.append(a)

                            # Procedure to find depedent and indepedent claims in all languages [EN, DE, FR] and union claims
                            # with regex word-key [in dict words{}]
                            for claims_arra in claims_arr:
                                for word in words["word"]:
                                    if re.search(word + " [0-9]", claims_arra):
                                        depedent.append(counter_dep)
                                        if (only_numerics(claims_arra[
                                                          claims_arra.find(word) + len(word):claims_arra.find(
                                                                  word) + len(word) + 3])):
                                            v = int(only_numerics(claims_arra[
                                                                  claims_arra.find(word) + len(word):claims_arra.find(
                                                                      word) + len(word) + 3]))
                                        if v in data:
                                            data[v].append(claims_arra[
                                                           claims_arra.find(word) + len(word) + 4:len(claims_arra) - 2])
                                            # data_numbers[v].append(counter_c)
                                        else:
                                            if v <= len(claims_arr):
                                                data[v] = [claims_arr[v - 1]]
                                                data[v].append(claims_arra[
                                                               claims_arra.find(word) + len(word) + 4:len(claims_arra)])
                                
                                # Compute depedenet and indepedent claims based on previous procedure
                                if counter_dep not in depedent:
                                    if counter_dep not in indepedent:
                                        indepedent.append(counter_dep)
                                counter_dep += 1

                            # Write close tags and extra depedent, indepedent and union tags    
                            writer.write("<CLAIM" + str(counter_c) + ">\n")
                            for text in claims_n1:
                                writer.write(str(text).strip() + "\n")
                            writer.write("</CLAIM" + str(counter_c) + ">\n")
                            writer.write("</CLAIMS>\n")
                            writer.write("<INDEPEDENT>\n")
                            writer.write(str(indepedent) + "\n")
                            writer.write("</INDEPEDENT>\n")
                            writer.write("<DEPEDENT>\n")
                            writer.write(str(depedent) + "\n")
                            writer.write("</DEPEDENT>\n")

                            # Write union tags
                            writer.write("<UNION> \n")
                            for t in data:
                                writer.write("\nUNION CLAIM " + str(t) + " :\n" + ', '.join(data[t]) + "\n")
                            writer.write("</UNION>\n")
                        
                        # Else continue
                        else:
                            # check if there is a case that is out of 3 cases
                            case4.append(ids[0]["ucid"])
                            continue


# Print some stats for patents and claims
print("Exoun claim:", c)
print("case1:", len(set(case1)))
print("case2:", len(set(case2)))
print("case3:", len(set(case3)))
print("case4:", len(set(case4)))
print("case3:", case3)
print("case4:", case4)

