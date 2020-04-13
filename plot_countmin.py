import pickle
import os
import numpy as np
import matplotlib.pyplot as plt


dat = {}
with open("output/"+'COUNTMIN_TOP_FREQ_English_all.pkl', "rb") as f:
    dat = pickle.load(f)
eng_c = dat['C']
eng_l = dat['L']


dat = {}
with open("output/"+'COUNTMIN_TOP_FREQ_American_all.pkl', "rb") as f:
    dat = pickle.load(f)
amer_c = dat['C']
amer_l = dat['L']

labels = []
for lab in eng_l:
    if lab not in labels:
        labels.append(lab)

for lab in amer_l:
    if lab not in labels:
        labels.append(lab)
x = np.arange(len(labels))
eng_counts = [0]*len(labels)
amer_counts = [0]*len(labels)
eng_err = [[0]*len(labels), [0]*len(labels)]
amer_err = [[0]*len(labels), [0]*len(labels)]

i = 0
for lab in labels:
    try:
        eng_index = eng_l.index(lab)
        eng_counts[i] = eng_c[eng_index]
        eng_err[0][i] = 22198326
    except:
        pass
    
    try:
        amer_index = amer_l.index(lab)
        amer_counts[i] = amer_c[amer_index]
        amer_err[0][i] = 61980592
    except:
        pass
    
    i += 1

width = 0.35  # the width of the bars
fig, ax = plt.subplots(figsize = (15, 8))
rects1 = ax.bar(x - width/2, eng_counts,  width, yerr = eng_err,capsize = 2, label='British English')
rects2 = ax.bar(x + width/2, amer_counts,  width, yerr = amer_err, capsize=2, label='American English')

ax.set_ylabel('Counts')
ax.set_title('Count-Min Top Frequency Words')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=70)
ax.legend()
plt.show()





