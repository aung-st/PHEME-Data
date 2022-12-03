# -*- coding: utf-8 -*-

import os, json
from os.path import basename
from pathlib import Path
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
from dateutil import parser
import time
import datetime

def get_rumourdata(path):
    rid = ""
    rumour_dict = {}
    for subdir, dirs, files in os.walk(path):
        print(subdir)
        # rumour_sdfiles = [os.path.join(subdir, pos_json) for pos_json in os.listdir(subdir) if (pos_json.endswith('.json')) and not(pos_json.startswith('._')) and ('rumours' in subdir)] 
        # nonrumour_sdfiles = [os.path.join(subdir, pos_json) for pos_json in os.listdir(subdir) if (pos_json.endswith('.json')) and not(pos_json.startswith('._')) and ('non-rumors' in subdir)] 
        if (('\\rumours\\' in subdir) and ("annotation.json" in os.listdir(subdir))):
            rid = basename(subdir)
            with open(os.path.join(subdir, "annotation.json"), encoding='utf8') as annotation_jfile:
                annotation_json = json.load(annotation_jfile)
            with open(os.path.join(subdir, "structure.json"), encoding='utf8') as structure_jfile:
                structure_json = json.load(structure_jfile)
            rid_dict = {
                "rid" : rid,
                "is_rumour" : annotation_json['is_rumour'],
                "category" : annotation_json['category'],
                "misinformation" : annotation_json['misinformation'],
                "true" : annotation_json['true'],
                "links" : annotation_json['links'],
                "is_turnaround" : annotation_json['is_turnaround'],
                "structure" : structure_json,
            }
            if not rumour_dict:
                rumour_dict = {
                    rid : rid_dict
                }
            else:
                rumour_dict[rid] = rid_dict
        if (('\\non-rumours\\' in subdir) and ("annotation.json" in os.listdir(subdir))):
            rid = basename(subdir)
            with open(os.path.join(subdir, "annotation.json"), encoding='utf8') as annotation_jfile:
                annotation_json = json.load(annotation_jfile)
            with open(os.path.join(subdir, "structure.json"), encoding='utf8') as structure_jfile:
                structure_json = json.load(structure_jfile)
            rid_dict = {
                "rid" : rid,
                "is_rumour" : annotation_json['is_rumour'],
                "structure" : structure_json,
            }
            if not rumour_dict:
                rumour_dict = {
                    rid : rid_dict
                }
            else:
                rumour_dict[rid] = rid_dict
        if ('source-tweets' in subdir):
            for pos_json in os.listdir(subdir):
                if ((pos_json.endswith('.json')) and not(pos_json.startswith('._'))):
                    with open(os.path.join(subdir, pos_json), encoding='utf8') as source_jfile:
                        source_json = json.load(source_jfile)
                    rid = str(source_json["id"])
                    text = source_json["text"]
                    created_at = parser.parse(source_json["created_at"])
                    ttime = time.mktime(datetime.datetime.strptime(source_json["created_at"], "%a %b %d %H:%M:%S +0000 %Y").timetuple())
                    # created_at = datetime.strftime(source_json["created_at"], "%a %b %d %H:%M:%S %z %Y")
                    cleaned_text = clean_text(text) #clean text
                    rumour_dict[rid].update({"text" : text, "cleaned_text" : cleaned_text, "ttime" : ttime, "created_at" : created_at, "json" : source_json})
                    # rumour_dict[rid].update({"text" : text, "cleaned_text" : cleaned_text, "created_at" : created_at, "json" : source_json})
        if ('reactions' in subdir):
            rid = basename(Path(subdir).parent)
            reaction_dict = {}
            for pos_json in os.listdir(subdir):
                if ((pos_json.endswith('.json')) and not(pos_json.startswith('._'))):
                    with open(os.path.join(subdir, pos_json), encoding='utf8') as reaction_jfile:
                        reaction_json = json.load(reaction_jfile)
                    react_id = str(reaction_json['id'])
                    if not reaction_dict:
                        reaction_dict = {
                            react_id : reaction_json
                        }
                    else:
                        reaction_dict[react_id] = reaction_json
            rumour_dict[rid].update({"reactions": reaction_dict})
    add_label(rumour_dict)
    print("Completed reading rumour data")
    return rumour_dict

def clean_text(text):
    text = text.strip().replace("\n", "") #remove whitespaces
    text = text.encode("ascii","ignore").decode()
    text = re.sub(r'\b[0-9]+\b', '', text).lower() #remove numbers and to lowercase
    text = text.translate(str.maketrans("","", string.punctuation)) #remove punctuation
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    filtered_tokens = [i for i in tokens if not i in stop_words]
    text = " ".join(filtered_tokens)
    return text

def read_rumourdata(path):
    rumour_dict = get_rumourdata(path)
    # print(rumour_dict)
    for rkey, value in rumour_dict.items() :
        for key, value in value.items() :
            print (key)
        print(rkey)

# def get_annotation(r_item, string = True):
def get_annotation(r_item, string = False):
    if r_item['is_rumour'] == 'nonrumour':
        if string:
            label = "nonrumour"
        else:
            label = 2
    elif 'misinformation' in r_item.keys() and 'true'in r_item.keys():
        if int(r_item['misinformation'])==0 and int(r_item['true'])==0:
            if string:
                label = "unverified"
            else:
                label = 3
        elif int(r_item['misinformation'])==0 and int(r_item['true'])==1 :
            if string:
                label = "true"
            else:
                label = 1
        elif int(r_item['misinformation'])==1 and int(r_item['true'])==0 :
            if string:
                label = "false"
            else:
                label = 0
        elif int(r_item['misinformation'])==1 and int(r_item['true'])==1:
            print ("OMG! They both are 1!")
            print(r_item['misinformation'])
            print(r_item['true'])
            label = None
    elif 'misinformation' in r_item.keys() and 'true' not in r_item.keys():
        # all instances have misinfo label but don't have true label
        if int(r_item['misinformation'])==0:
            if string:
                label = "unverified"
            else:
                label = 3
        elif int(r_item['misinformation'])==1:
            if string:
                label = "false"
            else:
                label = 0
    elif 'true' in r_item.keys() and 'misinformation' not in r_item.keys():
        print ('Has true not misinformation: ' + str(r_item['rid']))
        label = None
    else:
        print('No annotations: ' + str(r_item['rid']))
        label = None
    return label

def add_label(rumour_dict):
    for rkey, rvalue in rumour_dict.items() :
        # rvalue.update({"label": str(get_annotation(rvalue))})
        rvalue.update({"label": get_annotation(rvalue)})

def export_labelleddata(rumour_dict,name):
    rumour_dict = {k: v for k, v in sorted(rumour_dict.items(), key=lambda item: item[1]["created_at"])}
    rumour_file = open(name,"w")#write mode 
    for rkey, rvalue in rumour_dict.items() :
        if(rvalue['label'] != "None"):
            # rumour_file.write("\"" + rvalue['rid'] + "\",\"" + datetime.strftime(rvalue['created_at'], "%d %b %Y %H:%M:%S") + "\",\"" + rvalue['cleaned_text'] + "\",\"" + rvalue['label'] + "\"\n")
            rumour_file.write("\"" + str(rvalue['rid']) + "\",\"" + rvalue['created_at'].strftime("%d %b %Y %H:%M:%S") + "\",\"" + rvalue['cleaned_text'] + "\",\"" + str(rvalue['label']) + "\"\n")
    rumour_file.close()





def ContinuousIntervalSet(intervalL):
    maxInt = []
    tempInt = [intervalL[0]]
    for q in range(1,len(intervalL)):
        if intervalL[q]-intervalL[q-1] > 1:
            if len(tempInt) > len(maxInt):
                maxInt = tempInt
            tempInt = [intervalL[q]]
        else :
            tempInt.append(intervalL[q])
    if (len(tempInt) > len(maxInt)) :
        maxInt = tempInt
# 	if len(maxInt)==0:
# 		maxInt = tempInt
    return maxInt



def loadLabel(label, l1, l2, l3, l4):
    if label == 0: ## false rumour
       y_train = [1,0,0,0]
       l1 += 1
    if label == 1: ## true rumour
       y_train = [0,1,0,0] 
       l2 += 1
    if label == 2: ## non-rumour
       y_train = [0,0,1,0] 
       l3 += 1 
    if label == 3: ## unverified rumour
       y_train = [0,0,0,1] 
       l4 += 1
    return y_train, l1,l2,l3,l4       

#read_rumourdata("6392078\\all-rnr-annotated-threads\\charliehebdo-all-rnr-threads")
#name of my pheme dataset folder
rumour_dict = get_rumourdata("6392078\\all-rnr-annotated-threads\\sydneysiege-all-rnr-threads")
export_labelleddata(rumour_dict,"sydneysiege-all-rnr-threads.csv")
