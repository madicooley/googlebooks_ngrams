import matplotlib.pyplot as plt
import pickle
import os
import string
import numpy as np


def get_filename(query, collection):
    """
        Locates the desired file
        TODO: eventually change this to loop over all files to create plots and things
        TODO: better file querying
    """
    for filename in os.listdir('output'):
        if "_"+query+'.pkl' in filename and "_"+collection+"_" in filename:
            return filename
    print("ERROR: Could not locate desired file.")


def read_misra_results(query, collection):
    """
    Opens the pickle file with the results from running Misra
    The 'L' key has the labels--specific ngram
    The 'C' key has the corresponding counts
    """
    fname = get_filename(query, collection)
    
    dat = {}
    with open("output/"+fname, "rb") as f:
        dat = pickle.load(f)
        print(dat)
    return dat


def get_top_freq_words(dat, k):
    """
    Given data, find the top k most frequent words with associated counts
    """
    
    counts = np.array(dat['C'])
    labels = np.array(dat['L'])
    
    # indices of top k
    temp1 = np.argpartition(-counts, k)
    top_indices = temp1[:k]

    # count values
    temp2 = np.partition(-counts, k)
    top_count_values = -temp2[:k]
    
    # associated labels
    top_labels = [labels[i] for i in top_indices]
    
    print(top_indices)
    print(top_count_values)
    print(top_labels)
    
    return {'C':top_count_values, 'L':top_labels}
    

def plot(dat, collection, query):
    """
        Creates bar plot of the counts
    """
    x = np.arange(len(dat['C']))
    labels = dat['L']
    
    plt.bar(x, width=0.4, height=dat['C'])
    plt.xticks(x, labels, rotation=70)

    plt.ylabel('Counts')
    plt.xlabel('Labels')
    plt.title('Misra-Gries on '+collection+' "'+query+'" 1-grams')
    plt.show()
    

def compare_american_to_english(dat_eng, dat_amer, collection, collection_amer, query):
    """
        Plots the output from Misra-Gries on the specific query for both the 
        Enlish and American 1-grams. If the labels for each ended up the same, they
        are plotted next to each other. If one didnt output a label that
        the other did, the count for the former is set to 0.
    """
    # must reformat the data a bit to plot correctly
    labels = []
    for lab in dat_eng['L']:
        if lab not in labels:
            labels.append(lab)
    
    for lab in dat_amer['L']:
        if lab not in labels:
            labels.append(lab)
    
    x = np.arange(len(labels))
    
    eng_counts = [0]*len(labels)
    amer_counts = [0]*len(labels)

    print()
    print(labels)
    print(len(labels))
    
    i = 0
    for lab in labels:
        try:
            eng_index = dat_eng['L'].index(lab)
            eng_counts[i] = dat_eng['C'][eng_index]
        except:
            pass
        
        try:
            amer_index = dat_amer['L'].index(lab)
            amer_counts[i] = dat_amer['C'][amer_index]
        except:
            pass
        
        i += 1
    
    
    # NOTE below code from https://matplotlib.org/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
    
    width = 0.35  # the width of the bars
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, eng_counts, width, label='British English')
    rects2 = ax.bar(x + width/2, amer_counts, width, label='American English')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Counts')
    ax.set_xlabel('Labels')
    ax.set_title('Misra-Gries English vs. American "'+query+'" '+' 1-grams')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=70)
    ax.legend()


    # TODO figure out how to rotate these labels, they are too messy as is.
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax.annotate("{:.2e}".format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')


    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    plt.show()


def compare_misra_to_countmin():
    """
        NOTE: see code for compare_american_to_english() as an example
    """
    pass


def main():
    query = 'A'  # the letter of the ngram we want to read
    
    # British English
    collection = 'English'  # 'American' or 'English'
    dat_eng = read_misra_results(query, collection)
   
    # American
    collection_amer = 'American'  # 'American' or 'English'
    dat_amer = read_misra_results(query, collection_amer)
    
    # individual plots
    #plot(dat, collection, query)
    #plot(dat_amer, collection_amer, query)
    
    k = 10  # top 10 most frequent words
    dat_eng = get_top_freq_words(dat_eng, k)
    dat_amer = get_top_freq_words(dat_amer, k)
    
    compare_american_to_english(dat_eng, dat_amer, collection, collection_amer, query)

    # TODO implement compare_misra_to_countmin()
    

if __name__ == "__main__":
    main()
    
    
