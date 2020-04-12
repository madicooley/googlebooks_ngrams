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
L = [0]*n_top_words*10  # eps = 0.01
C = [0]*n_top_words*10


def get_stream(query, collection):
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

    print("starting misras")
    # loop over the stream.
    count = 0
    if query == 'all':          # loop over entire db
        start = time.time()
        for i in col.find(): 
            misra_greis(i["ngram"], i["match_count"])
            count += 1
        end = time.time()
    else:                       # loops over ngrams for ONE letter.
        start = time.time()
        for i in col.find({'ngram':{'$regex':query}}): 
            misra_greis(i["ngram"], i["match_count"])
            count +=1
            
        end = time.time()
     
    print("Misra-Gries TIME : ", (end - start)/60.0, " minutes")
    print('Total # of documents considered = ', count)
    print(L, C)
    

def misra_greis(single_ngram, match_count):
    """
        This version is much quicker than the slow version. 
    
    """
    ai = str(single_ngram).lower()
    
    #for i in range(match_count):
    inL = False
    inL_index = None
    
    # find ai in the list of labels
    for j in range(len(L)):
        if ai == L[j]:
            inL = True
            inL_index = j
    
    spot_found = False
    if inL:
        C[inL_index] += match_count
    else:
        for j in range(len(C)):
            if C[j] == 0:   # an empty space in the lables/counts
                L[j] = ai
                C[j] = match_count
                spot_found = True
                break
        
        # theres not an open space for the current stream val
        if spot_found == False:
            # find minimum count in C, need index and value
            min_ = min(C)
            index = C.index(min(C))  # index of the minimum value
            if min_ - match_count <= 0:
                val = match_count - min_
                if val == 0:
                    val = 1
                C[index] = val
                L[index] = ai
            else:
                for k in range(len(C)):
                    C[k] -= match_count   # all counters are non-zero and no labels match, decrement all


def misra_greis_slow(single_ngram, match_count):
    """
    This is more similar to the original misra alg. However, it is much slower, 
    takes around and hour for 'A'. 
    """
    ai = single_ngram
    
    for i in range(match_count):
        inL = False
        inL_index = None
        
        for j in range(len(L)):
            if ai == L[j]:
                inL = True
                inL_index = j
        
        all_zeros = True
        if inL:
            C[inL_index] += 1
        else:
            for j in range(len(C)):
                if C[j] == 0:
                    L[j] = ai
                    C[j] = 1
                    all_zeros = False
                    break
            if all_zeros == True:
                for k in range(len(C)):
                    C[k] -= 1   # all counters are non-zero and no labels match, decrement all



def save_to_file(query, collection):
    """
        Saves Misra output to a file as to not rerun lengthy experiments unecessarily
    """
    if not os.path.exists("output"):  # if output dir doesnt exists, creates it
        os.makedirs("output")
        
    # TODO probably need to update the replacing
    query_value = query.replace("^", "")
    with open("output/MISRA_"+collection+"_"+query_value+".pkl", "wb") as fp:   #Pickling
        obj = {'L':L, 'C':C}
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
    
    get_stream(QUERY, collection)  
    
    save_to_file(QUERY, collection)


if __name__ == "__main__":
    main()
    
