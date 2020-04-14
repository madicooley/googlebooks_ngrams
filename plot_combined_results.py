import matplotlib.pyplot as plt
import pickle
import os
import string
import numpy as np
import matplotlib.pyplot as plt

def read_results(collection, n_top_words):
    dat = {}
    with open('output/TWOPASS_MISRA_'+collection+'_all.pkl', "rb") as f:
        dat = pickle.load(f)
    counts = dat['C']
    labels = dat['L']
    counts, labels = zip(*sorted(zip(counts, labels), reverse=True))
    counts = counts[: n_top_words]
    labels = labels[: n_top_words]

    dat = {}
    with open('output/COUNTMIN_TWOPASS_MISRA_TOPWORDS_'+collection+'_all.pkl', "rb") as f:
        dat = pickle.load(f)
    upper_bound = dat['C']
    upper_bound = upper_bound[:n_top_words]
    if collection == 'English':
        lower_bound = [22198326] * n_top_words
    else:
        lower_bound = [61980592] * n_top_words

    #dat = {}
    #with open("output/"+'MISRA_'+collection+'_all.pkl', "rb") as f:
    #    dat = pickle.load(f)
    #tmp_counts = dat['C']
    #tmp_labels = dat['L']
    #lower_bound = [0]*n_top_words
    #for i, lab in enumerate(tmp_labels):
    #    if lab in labels:
    #        lower_bound[labels.index(lab)] = tmp_counts[i]

    return (counts, labels, [lower_bound, upper_bound])

def plot():
    eng_c, eng_l, eng_e = read_results('English', 20)
    amer_c, amer_l, amer_e = read_results('American', 20)

    labels = []
    for lab in eng_l:
        if lab not in labels:
            labels.append(lab)
    
    for lab in amer_l:
        if lab not in labels:
            labels.append(lab)

    x = np.arange(len(labels))

    eng_counts = [0]*len(labels)
    eng_errors = [[0]*len(labels), [0]*len(labels)]
    amer_counts = [0]*len(labels)
    amer_errors = [[0]*len(labels), [0]*len(labels)]
    
    i = 0
    for lab in labels:
        try:
            eng_index = eng_l.index(lab)
            eng_counts[i] = eng_c[eng_index]
            eng_errors[1][i] = eng_e[1][eng_index]-eng_c[eng_index]
            eng_errors[0][i] = eng_e[0][eng_index]-eng_errors[1][i]
            
        except:
            pass
        
        try:
            amer_index = amer_l.index(lab)
            amer_counts[i] = amer_c[amer_index]
            amer_errors[1][i] = amer_e[1][eng_index]-amer_c[amer_index]
            amer_errors[0][i] = amer_e[0][eng_index] - amer_errors[1][i]
        except:
            pass
        
        i += 1
    width = 0.35  # the width of the bars
    fig, ax = plt.subplots(figsize = (15, 8))
    rects1 = ax.bar(x - width/2, eng_counts,  width, yerr = eng_errors, capsize=2, label='British English')
    rects2 = ax.bar(x + width/2, amer_counts,  width, yerr = amer_errors, capsize=2, label='American English')

    # Add some text forr labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Counts')
    #ax.set_xlabel('Labels')
    ax.set_title('Two-Pass Misra-Gries Top Frequency Words with Count-Min Sketch Error Bounds')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=70)
    ax.legend()
    plt.show()
    


def main():
    k = 20  # top 10 most frequent words
    plot()
    

if __name__ == "__main__":
    main()
    
    
