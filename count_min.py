import pymongo as py
import os
import pickle
import hashlib
import string 
import random
import heapq
import pandas as pd
import numpy as np
import time


n_top_words = 10

class CountMinSketch:
    
    def __init__(self, t, k):
        # t: number of hash functions
        # k: number of counters per hash function
        self.t = t
        self.k = k
    
    def fit(self, col):
        
        # create a list of seeds for the hash functions
        self.s = []
        for _ in range(self.t):
            # generate a random string of length 5 as a seed
            self.s.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) )
        
        # a 2d array of counters
        self.counters = [[0 for _ in range(self.k)] for _ in range(self.t)]
        
        # the total number of documents
        self.total_doc_count = 0
        self.total_match_count = 0
        
        # loop through all documents in a collection
        for document in col.find():
            # use the lowercase of the ngram as input
            c = document['ngram'].lower()
            self.total_doc_count += 1
            self.total_match_count += document['match_count']
            
            # increment on counters for each hash function
            for j in range(self.t):
                nCounter = int(hashlib.sha256((self.s[j]+c).encode('utf-8')).hexdigest(), 16) % self.k
                self.counters[j][nCounter] += document['match_count']
        return
    
    def query(self, c):
        c = c.lower()
        self.minCount = float('inf')
        for j in range(self.t):
            nCounter = int(hashlib.sha256((self.s[j]+c).encode('utf-8')).hexdigest(), 16) % self.k
            if self.counters[j][nCounter] < self.minCount:
                self.minCount = self.counters[j][nCounter]
        return self.minCount


def get_stream(query, collection):
    client = py.MongoClient('localhost', 27017)
    
    # NOTE: probably will need to change these for your names
    db = client.NGRAM  
    
    if collection == 'American':
        col = db.American_1gram      # american english
    elif collection == 'English':
        col = db.English_1gram       # british english
    print(col)
    print("Collection: ", collection)

    # to check connection to db
    print('Query: ', query)
    item = col.find_one({"ngram": {'$regex':query}})       
    print("Checking Connection: ", item)
    
    if item == None:
        print("Connection unsuccessful, aborting")
        return 
    print ('*'*50)

    need_temp = True
    if query == 'all':
        need_temp = False
    else:
        print ('creating temporary collection')
        if collection == 'American':
            db.American_1gram.aggregate([ { '$match':{ 'ngram': { '$regex': query }} }, { '$out': "temp" } ])
        elif collection == 'English':
            db.English_1gram.aggregate([ { '$match':{ 'ngram': { '$regex': query }} }, { '$out': "temp" } ])  
        col = db.temp


    print("starting count-min")
    start = time.time()
    cms = CountMinSketch(10, 2000)
    cms.fit(col)
    end = time.time()
    print("Count-Min TIME : ", (end - start)/60.0, " minutes")
    print('Total # of documents considered = ', cms.total_doc_count)
    print ('*'*50)

    print ('getting top frequency words')
    # query all documents to find the top frequency words
    seen = set()
    top_freq_heap = []
    for doc in col.find():
        word = doc['ngram'].lower()
        if word in seen:
            continue
        seen.add(word)
        freq = cms.query(word)
        if len(top_freq_heap) < n_top_words:
            heapq.heappush(top_freq_heap, [freq, word])
        elif freq > top_freq_heap[0][0]:
            heapq.heapreplace(top_freq_heap, [freq, word])
    top_freq_heap.sort()
    top_freq_heap = top_freq_heap[::-1]
    top_freq_df = pd.DataFrame(top_freq_heap, columns = ['count', 'label']) 
    print(top_freq_df)
    print ('*'*50)

    print ('query misra-greis top words')
    if query != 'all':
        q = query[3]
    for filename in os.listdir('output'):
        if "_"+q+'.pkl' in filename and "MISRA_"+collection+"_" in filename:
            fname = filename
            break
    misra_results = {}
    with open("output/"+fname, "rb") as f:
        misra_results = pickle.load(f)
    misra_count = misra_results['C']
    misra_label = misra_results['L']
    misra_count, misra_label = zip(*sorted(zip(misra_count, misra_label), reverse=True))
    countmin_count = []
    for word in misra_label[:n_top_words]:
        freq = cms.query(word)
        countmin_count.append(freq)
    print(misra_label[:n_top_words], countmin_count)

    if need_temp:
        db.temp.drop()


    if not os.path.exists("output"):  # if output dir doesnt exists, creates it
        os.makedirs("output")
        
    # TODO probably need to update the replacing
    query_value = query[3]
    with open("output/COUNTMIN_TOP_FREQ_"+collection+"_"+query_value+".pkl", "wb") as fp:   #Pickling
        obj = {'L':top_freq_df['label'].to_list(), 'C':top_freq_df['count'].to_list()}
        pickle.dump(obj, fp)

    with open("output/COUNTMIN_MISRA_TOPWORDS_"+collection+"_"+query_value+".pkl", "wb") as fp:   #Pickling
        obj = {'L':misra_label[:n_top_words], 'C':countmin_count}
        pickle.dump(obj, fp)


def main():
    # NOTE set QUERY = 'all' to run on entire db
    QUERY = '^[aA]' # to query the ngrams which start with a specific letter, follow this format
    collection = 'English'  # 'American' or 'English'
    
    get_stream(QUERY, collection)  


if __name__ == "__main__":
    main()
    
