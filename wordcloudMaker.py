# -*- coding: utf-8 -*-


import numpy as np
import pickle
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd


file1 = "output\COUNTMIN_TOP_FREQ_American_all.pkl"
file2 = "output\COUNTMIN_TOP_FREQ_English_all.pkl"

with open(file1, 'rb') as f:
    dat = pickle.load(f)
    
counts = dat['C']
labels = dat['L']
    
data = np.array([labels, counts]).T
data = pd.DataFrame(data=data, columns=["words", "counts"])
d = {}
for a, x in data.values:
    d[a] = int(x)

wordcloud = WordCloud().generate_from_frequencies(d)
plt.figure(figsize=(20,20))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

with open(file2, 'rb') as f:
    dat = pickle.load(f)
    
counts = dat['C']
labels = dat['L']
    
data = np.array([labels, counts]).T
data = pd.DataFrame(data=data, columns=["words", "counts"])
d = {}
for a, x in data.values:
    d[a] = int(x)

wordcloud = WordCloud().generate_from_frequencies(d)
plt.figure(figsize=(20,20))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
