import nltk
from nltk.corpus import stopwords
import pymongo as py
import pickle
import os
import string
import re
import time
import argparse

n_top_words = 10
#k_min = 20
#L = [0]*n_top_words*10  # eps = 0.01
#C = [0]*n_top_words*10

C_true = [0]*n_top_words*10


def get_filename(query, collection):
    """
        Locates the desired file
    """
    query_value = query.replace("^", "")
    for filename in os.listdir('output'):
        if "_"+query_value+'.pkl' in filename and "_"+collection+"_" in filename:
            return filename
    print("ERROR: Could not locate desired file.")


def read_misra_results(query, collection):
    """
    Opens the pickle file with the results from running Misra
    The 'L' key has the labels--specific ngram
    The 'C' key has the corresponding counts
    """
    fname = get_filename(query, collection)
    print("***", fname)
    
    dat = {}
    with open("output/"+fname, "rb") as f:
        dat = pickle.load(f)
        print(dat)
    return dat


def get_stream(dat, query, collection):
    client = py.MongoClient('localhost', 27017)
    
    # NOTE: probably will need to change these for your names
    db = client.google_books_ngram  
    
    if collection == 'American':
        col = db.American_1gram      # american english
    elif collection == 'English':
        col = db.British_1gram       # british english
    print(col)
    print("Collection: ", collection)

    # to check connection to db
    print('Query: ', query)
    item = col.find_one({"ngram": {'$regex':query}})       
    print("Checking Connection: ", item)
    
    if item == None:
        print("Connection unsuccessful, aborting")
        return 

    print("starting 2 misras")
    # loop over the stream.
    count = 0
    if query == 'all':          # loop over entire db
        start = time.time()
        for i in col.find(): 
            second_pass_misra_greis(dat, i["ngram"], i["match_count"])
            count += 1
        end = time.time()
    else:                       # loops over ngrams for ONE letter.
        start = time.time()
        for i in col.find({'ngram':{'$regex':query}}): 
            second_pass_misra_greis(dat, i["ngram"], i["match_count"])
            count +=1
            
        end = time.time()
    
    print(C_true)
    print("Two Pass Misra-Gries TIME : ", (end - start)/60.0, " minutes")
    print('Total # of documents considered = ', count)
    

def second_pass_misra_greis(dat, single_ngram, match_count):
    i = 0
    for key in dat['L']:
        if single_ngram == key:
            C_true[i] += match_count
        i += 1


def save_to_file(dat, query, collection):
    """
        Saves Misra output to a file as to not rerun lengthy experiments unecessarily
    """
    if not os.path.exists("output"):  # if output dir doesnt exists, creates it
        os.makedirs("output")
        
    query_value = query.replace("^", "")
    with open("output/TWOPASS_MISRA_"+collection+"_"+query_value+".pkl", "wb") as fp:   #Pickling
        obj = {'L':dat['L'], 'C':C_true}
        pickle.dump(obj, fp)


def get_args():
    parser = argparse.ArgumentParser(description='None')
    parser.add_argument('-q', "--query", action='store', help="", required=True)
    parser.add_argument('-c', '--collection', action='store', help="", required=True)

    args = vars(parser.parse_args())

    return args


def main():
    args = get_args()
    print(args)
    
    # NOTE set QUERY = 'all' to run on entire db
    # to query the ngrams which start with a specific letter, follow this format
    #QUERY = '^[aA]'  
    #collection = 'American'  # 'American' or 'English'
    
    QUERY = args['query']
    collection = args['collection']
    
    dat = read_misra_results(QUERY, collection)
    
    get_stream(dat, QUERY, collection)  
    
    save_to_file(dat, QUERY, collection)


if __name__ == "__main__":
    main()
    
