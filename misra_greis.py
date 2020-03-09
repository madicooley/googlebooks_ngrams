import nltk
from nltk.corpus import stopwords
import pymongo as py
import pickle
import os
import string
import re
import time


k_min_1 = 20
L = [0]*k_min_1
C = [0]*k_min_1


def clean(col):
    """
        Mario's cleaning code
    """

    print("cleaning")
    
    # Removes all documents with special characters
    regex = re.compile('[`,.-@_!#$%^&*()<>?/\|}{~:+=]') 
    query = {'ngram': { "$regex": regex }}     
    x = col.delete_many(query)
    print(x.deleted_count, " special char documents deleted.")                   

    # Removes all documents with numbers
    regex = re.compile('[0123456789]') 
    query = {'ngram': { "$regex": regex }}     
    x = col.delete_many(query)
    print(x.deleted_count, " numerical documents deleted.") 

    # Remove all documents that are stopwords
    sw = stopwords.words("english")
    list.sort(sw)

    for s in sw:
        lw = s
        Uw = s.upper()
        Cw = s.capitalize()
        query = {'ngram': lw }
        col.delete_many(query)
        query = {'ngram': Uw }
        col.delete_many(query)
        query = {'ngram': Cw }
        col.delete_many(query)
        print('Deleting ', s)
        
    print('Done!')
    
    return col


def get_stream(query, collection, clean_col=True):
    client = py.MongoClient('localhost', 27017)
    
    # NOTE: probably will need to change these for your names
    db = client.google_books_ngram  
    
    if collection == 'American':
        col = db.American_1gram      # american english
    elif collection == 'English':
        col = db.english_1gram       # english
    print(col)
    print("Collection: ", collection)

    # to check connection to db
    print('Query: ', query)
    item = col.find_one({"ngram": {'$regex':query}})       
    print("Checking Connection: ", item)
    
    if item == None:
        print("Connection unsuccessful, aborting")
        return 
    
    if clean_col:
        col = clean(col)             # if collection needs cleaning

    print("starting misras")
    # loop over the stream.
    count = 0
    if query == 'all':          # loop over entire db
        start = time.time()
        for i in col.find(): 
            misra_greis(i["ngram"])
            count += 1
        end = time.time()
    else:                       # loops over ngrams for ONE letter.
        start = time.time()
        for i in col.find({'ngram':{'$regex':query}}): 
            misra_greis(i["ngram"])
            count +=1
        end = time.time()
     
    print("Misra-Gries TIME : ", (end - start)/60.0, " minutes")
    print('Total # of documents considered = ', count)
    print(L, C)
    

def misra_greis(single_ngram):
    ai = single_ngram
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
        
    query_value = query.replace("^", "")
    with open("output/MISRA_"+collection+"_"+query_value+".pkl", "wb") as fp:   #Pickling
        obj = {'L':L, 'C':C}
        pickle.dump(obj, fp)


def main():
    # NOTE set QUERY = 'all' to run on entire db
    QUERY = '^A'  # to query the ngrams which start with a specific letter, follow this format
    collection = 'English'  # 'American' or 'English'
    
    get_stream(QUERY, collection, clean_col=False)  # set clean to False if you've already cleaned the col
    
    save_to_file(QUERY, collection)


if __name__ == "__main__":
    main()
    
