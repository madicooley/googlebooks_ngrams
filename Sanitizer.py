# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 21:39:28 2020

@author: mario
"""

import pymongo as py
import re

client = py.MongoClient('localhost', 27017)
db = client.NGRAM
col = db.American_1gram

# Remove all documents that are stopwords
#import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords
sw = stopwords.words("english")
list.sort(sw)

for s in sw:
  # Does not use case-insenstive in regex as it performs far slower
  # than just query 3x
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

# Removes all documents with special characters
print('deleteing special characters')
regex = re.compile('[`,.-@_!#$%^&*()<>?/\|}{~:+=]') 
query = {'ngram': { "$regex": regex }}     
x = col.delete_many(query)
print(x.deleted_count, " special char documents deleted.")                   

# Removes all documents with numbers
print('deleting numbers')
regex = re.compile('[0-9]') 
query = {'ngram': { "$regex": regex }}     
x = col.delete_many(query)
print(x.deleted_count, " numerical documents deleted.") 

# Removes all documents with accents
print('deleting numbers')
regex = re.compile('[À-ú]') 
query = {'ngram': { "$regex": regex }}     
x = col.delete_many(query)
print(x.deleted_count, " accented documents deleted.") 

print('Done!')  
