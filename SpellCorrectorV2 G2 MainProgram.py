import re
from collections import Counter
import numpy as np
import pandas as pd
import math
import random
import numpy as np
import pandas as pd
import nltk
import Candidates
import OOV
import Ngram
import ErrorModel
import string 

# Read file
with open("econ_corpus.txt", "r", encoding = 'ISO-8859-1') as f: #Coca_corpus.txt | econ_corpus vic updated 191220.txt | StockExchange.txt 
    data = f.read()

#Preprocess file    
data = re.sub(r'[^A-Za-z\.\?!\']+', ' ', data) #remove special character
data = re.sub(r'\b(?:[A-Z]{3,}\b|(?:[A-Za-z]\.){2,})\s*', ' ',data)# removes 3 or more capital letters e.g. XYZ or X.Y.Z. 

sentences = re.split(r'[\.\?!]+[ \n]+', data) #split data into sentences
sentences = [s.strip() for s in sentences] #Remove leading & trailing spaces
sentences = [s for s in sentences if len(s) > 0] #Remove whitespace

tokenized_sentences=[]

# this is the new tokenisation for sentences. This will keep all words including "shouldn't". Removes numbers and non words like e.g. and etc. 
for sentence in sentences: 
        non_words = ['etc'] 
        # Convert to lowercase letters
        sentence = sentence.lower() 
        
        # Convert into a list of words
        tokenized = re.findall("[\w']+", sentence) #tokenises words. keeps numbers keeps shouldn't but has e and g in list from e.g. 
        
        # Remove random letters leftover from tokenising. 
        one_word = list(string.ascii_lowercase[0:26])
        one_word.remove('a')
        one_word.remove('i')
        
        for i in list(tokenized):
            if i in one_word:
                tokenized.remove(i)
                
        # remove non_words i.e. 'etc'
        for word in list(tokenized): 
                if word in non_words: 
                    tokenized.remove(word) 
        # append the list of tokenized_sentences to the list of lists
        tokenized_sentences.append(tokenized) 

# Get Vocabulary
vocabulary = list(set(OOV.get_nplus_words(tokenized_sentences, 2)))

# Replace less frequent word by <UNK>
processed_sentences = OOV.replace_words_below_n_by_unk(tokenized_sentences, 2)

# Get the unigram and bigram count to be used in language model
unigram_counts = Ngram.n_grams_dict(processed_sentences, 1)
bigram_counts = Ngram.n_grams_dict(processed_sentences, 2)

# Calculate N-gram probability given the pair of current word and previous_n_words
def get_probability(previous_n_words, word, 
                         previous_n_gram_dict, n_gram_dict, vocabulary_size, k=1.0):
  
    assert type(previous_n_words) == list

    # convert list to tuple to use it as a dictionary key
    previous_n_words = tuple(previous_n_words,)
    
    previous_n_words_count = previous_n_gram_dict[previous_n_words] if previous_n_words in previous_n_gram_dict else 0

    # k-smoothing
    denominator = previous_n_words_count + k*vocabulary_size

    # Define n plus 1 gram as the previous n-gram plus the current word as a tuple
    n_gram = previous_n_words + (word,)

    n_gram_count = n_gram_dict[n_gram] if n_gram in n_gram_dict else 0
   
    # smoothing
    numerator = n_gram_count + 1

    probability = numerator/denominator
    
    
    return probability

#calculate individual probability with n candidate
def get_corrections(previous_n_words_i, word, vocab, n=2, verbose = False):
    
    assert type(previous_n_words_i) == list
    corpus = ' '.join(vocabulary)
    suggestions = []
    n_best = []
    ### Convert to UNK if word not in vocab
    previous_n_words = []
    for w in previous_n_words_i:
        if w not in vocabulary:
            previous_n_words.append('<unk>')
        else:
            previous_n_words.append(w)
            
    ##Suggestions include input word only if the input word in vocab
    if word in vocab:    
        suggestions = [word] + list(Candidates.edit_one_letter(word).intersection(vocabulary)) or list(Candidates.edit_two_letters(word).intersection(vocabulary)) 
    else:
        suggestions = list(Candidates.edit_one_letter(word).intersection(vocabulary)) or list(Candidates.edit_two_letters(word).intersection(vocabulary)) 
        
    words_prob = {}
    for w in suggestions: 
        # To make sure all suggestions is within edit distance of 2
        _, min_edits = Candidates.min_edit_distance(' '.join(word),w)
        if not word in vocab: ##use error model only when it is non word error
            if min_edits <= 2:
                edit = ErrorModel.editType(w,' '.join(word))
                if edit:##Some word cannot find edit
                    if edit[0] == "Insertion":
                        error_prob = ErrorModel.channelModel(edit[3][0],edit[3][1], 'add',corpus)
                    if edit[0] == 'Deletion':
                        error_prob = ErrorModel.channelModel(edit[4][0], edit[4][1], 'del',corpus)
                    if edit[0] == 'Reversal':
                        error_prob = ErrorModel.channelModel(edit[4][0], edit[4][1], 'rev',corpus)
                    if edit[0] == 'Substitution':
                        error_prob = ErrorModel.channelModel(edit[3], edit[4], 'sub',corpus)
                else:
                    error_prob = 1
            else:
                error_prob = 1
        else:
            error_prob = 1
        language_prob = get_probability(previous_n_words, w, 
                        unigram_counts, bigram_counts, len(vocabulary), k=1.0)
            
        words_prob[w] = math.log(language_prob,(10)) + math.log(error_prob,(10))
        
    n_best = Counter(words_prob).most_common(n)
    
    if verbose: print("entered word = ", word, "\nsuggestions = ", suggestions) #for debugging purpose set verbose to True
    
    return n_best

# GUI CREATION THROUGH PYTHON'S TKINTER LIBRARY
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkfilterlist import FilterList
import operator
import csv


# creates a base GUI window
root = Tk() 

# creating fixed geometry of the tkinter window with dimensions 690x820
root.geometry("690x820") 
root.configure(background = "light blue")

root.title("CT052-3-M-NLP Group Assignment") # Adding a title to the GUI window.
Label(root, text = "GROUP TWO Spelling Checker", fg = "snow", bg = "steel blue", font = "Arial 11 bold italic", height = 1, width = 200).pack()
Label(root, text = "Instructions: ",fg = "gray2", bg = "light blue", font="Arial 10 italic", anchor="w",  height = 1, width = 300).place(x=15, y=30) #NEW 211220 
Label(root, text = "Key in the paragraph to be check & press 'Submit' button.", fg = "gray2", bg = "light blue", font="Arial 10 italic", anchor="w",  height = 1, width = 300).place(x=15, y=48) #NEW 211220 
Label(root, text = "Highlight the underlined WRONG spelled word with mouse.", fg = "gray2", bg = "light blue", font="Arial 10 italic", anchor="w",  height = 1, width = 300).place(x=15, y=67)  #NEW 211220 
Label(root, text = "Right click mouse button & click suggest", fg = "gray2", bg = "light blue", font="Arial 10 italic", anchor="w",  height = 1, width = 300).place(x=15, y=86 ) #NEW 211220 

# function to retrieve the sentence typed by a user & pass the input through get_corrections() to check spellings
tokenized_sentence = []
non_real_word = []

clicked=StringVar()
def getInput():
    global tokenized_sentence
    # Preprocess the original text input to get clean input
    sentenceValues = entredSentence.get('1.0', '50.0') # get the input sentence
    acronym_remove = re.sub(r'\b(?:[A-Z]{3,}\b|(?:[A-Za-z]\.){2,})\s*', ' ',sentenceValues) #removes 3 or more capital letters e.g. XYZ or X.Y.Z. Line 24 is redundant
    sentenceValues = sentenceValues.lower() #then only convert to lower case so that outputSentence.insert(END, sentenceValues) receives correct input
    tokenized = re.findall("[\w']+", acronym_remove) #tokenises words. keeps numbers keeps shouldn't but has e and g in list from e.g. 
    tokenized_sentence = [x.lower() for x in tokenized] # lower case the words in tokenized. Now it will be the same case except dont have acronyms. 

    #delete letters after tokenisation except for a and i. 
    import string 
    one_word = list(string.ascii_lowercase[0:26])
    one_word.remove('a')
    one_word.remove('i')

    # remove letters in one_word
    for i in list(tokenized_sentence):
        if i in one_word:
            tokenized_sentence.remove(i)
    
    # remove non words like etc 
    non_words = ['etc'] 
    for word in list(tokenized_sentence):
        if word in non_words:
            tokenized_sentence.remove(word)
    
    outputSentence.delete(0.0, 'end')
    outputSentence.insert(END, sentenceValues)  
    
    # tokenize the sentence and save the values to tokenizedWords variable
    tokenized_sentence = ['<s>']+ tokenized_sentence
    
    # define TP TN FP FN for non word error detection
    TP_NWE = 0 # Number of words with spelling errors for which the spell checker gave the correct suggestion
    TN_NWE = 0 # Number of correct words that the spell checker did not flag as having spelling errors and no suggestions were made
    FP_NWE = 0 # Number of words (with/without spelling errors) for which the spell checker made suggestions, and for those,|#either the suggestion is not needed (in the case of non-existing errors) or the suggestion is incorrect if|#indeed there was an error in the original word.
    FN_NWE = 0 # #Number of words with spelling errors that the spell checker did not flag as having spelling errors or did not
               # provide any suggestions
               
    # define TP TN FP FN for real word error detection
    TP_RWE = 0 # Number of words with spelling errors for which the spell checker gave the correct suggestion
    TN_RWE = 0 # Number of correct words that the spell checker did not flag as having spelling errors and no suggestions were made|
    FP_RWE = 0 # Number of words (with/without spelling errors) for which the spell checker made suggestions, and for those,|#either the suggestion is not needed (in the case of non-existing errors) or the suggestion is incorrect if|#indeed there was an error in the original word.
    FN_RWE = 0 # #Number of words with spelling errors that the spell checker did not flag as having spelling errors or did not
               # provide any suggestions

    not_in_corpus=[]
    real_word_error=[]
    for word in tokenized_sentence[1:]:
        if word not in vocabulary:
            not_in_corpus.append(word)  # Saving non real word to not_in_corpus list.
           
    for word in tokenized_sentence[1:]:
        if word in vocabulary: 
            index=tokenized_sentence.index(word)
            candidate_words = get_corrections([tokenized_sentence[index-1]], word, vocabulary, n=1, verbose=False)
            if candidate_words[0][0] != word :
                real_word_error.append(word) # saving a real & existing word to real_word_error
     
    # Checking for non_word errors from the input sentence typed by a user
    options=[]
    rwe_detected = [] #list of real word errors detected by system
    nwe_detected = [] #list of non word errors detected by system
     
    for word in not_in_corpus:
        
        offset = '+%dc' % len(word) # +5c (5 char) its calculate how many character in word & convert to numeric
    
        # search word from first char (1.0) to the end of text (END)
        pos_start = entredSentence.search(word, '1.0', END)
        
        if (len(pos_start) != 0): 
            nwe_detected.append(word) 
            TP_NWE += 1 
        # check if the word has been found
        while pos_start:
        
            # create end position by adding (as string "+5c") number of chars in searched word 
            pos_end = pos_start + offset
        
            # add red tag 
            entredSentence.tag_add('red_tag', pos_start, pos_end)
            #b.append(word)
        
            # search again from pos_end to the end of text (END)
            pos_start = entredSentence.search(word, pos_end, END)
        
        options.append(word) 
    
    # checking for real word error from the input sentence by a user
    for word in real_word_error:
        offset = '+%dc' % len(word) # +5c (5 chars) its calculate how many character in word & convert to numeric
    
        # search word from first char (1.0) to the end of text (END)
        pos_start = entredSentence.search(word, '1.0', END)
        
        if (len(pos_start) != 0): 
            rwe_detected.append(word) 
            TP_RWE += 1 
            
        # check if the word has been found
        while pos_start:
        
            # create end position by adding (as string "+5c") number of chars in searched word 
            pos_end = pos_start + offset
        
            # add blue tag
            entredSentence.tag_add('blue_tag', pos_start, pos_end)
            
        
            # search again from pos_end to the end of text (END)
            pos_start = entredSentence.search(word, pos_end, END)
        
        options.append(word)   
                      
    #Real word error detection
    for word in rwe_detected: 
        if word in vocabulary: 
            FP_RWE += 1 
                        
    for word in rwe_detected:
        if word not in real_word_error:
            FN_RWE +=1 
            
    for word in tokenized_sentence[1:]: 
        if word not in rwe_detected:
            TN_RWE += 1 
    
    # Non word error detection
    for word in nwe_detected: 
        if word in vocabulary: 
            FP_NWE += 1 
                        
    for word in nwe_detected:
        if word not in not_in_corpus:
            FN_NWE +=1 
            
    for word in tokenized_sentence[1:]: 
        if word not in nwe_detected:
            TN_NWE += 1 
            
    
    # Evaluate performance of real word error detection
    if (TP_RWE + FN_RWE) == 0: 
        print("\n###### Evaluation of Non-word Error Detection ######") 
        print("\nThere were no real word errors that were detected.") 
    else: 
        acc_RWE = (TP_RWE + TN_RWE)/ (TP_RWE + TN_RWE + FP_RWE + FN_RWE) 
        prec_RWE = TP_RWE / (TP_RWE + FP_RWE)
        recall_RWE = TP_RWE / (TP_RWE + FN_RWE) 
        fmeasure_RWE = (2 * prec_RWE * recall_RWE) / (prec_RWE + recall_RWE) 
        print("\n###### Evaluation of Real Word Error Detection ######") 
        print("\nTP:", TP_RWE) 
        print("TN:", TN_RWE) 
        print("FP:", FP_RWE) 
        print("FN:", FN_RWE) 
        print('Accuracy:', acc_RWE*100,'%') 
        print('Precision:', prec_RWE*100,'%') 
        print('Recall:', recall_RWE*100,'%') 
        print('F-measure:', fmeasure_RWE*100,'%') 
    
    #calculate performance of non word error detection
    if (TP_NWE + FN_NWE) == 0: 
        print("\n###### Evaluation of Non-word Error Detection ######")
        print("\nThere were no non-word errors that were detected.") 
    else: 
        acc_NWE = (TP_NWE + TN_NWE)/ (TP_NWE + TN_NWE + FP_NWE + FN_NWE) 
        prec_NWE = TP_NWE / (TP_NWE + FP_NWE)
        recall_NWE = TP_NWE / (TP_NWE + FN_NWE) 
        fmeasure_NWE = (2 * prec_NWE * recall_NWE) / (prec_NWE + recall_NWE) 
        print("\n###### Evaluation of Non-word Error Detection ######")
        print("\nTP:", TP_NWE)
        print("TN:", TN_NWE) 
        print("FP:", FP_NWE) 
        print("FN:", FN_NWE) 
        print('Accuracy:', acc_NWE*100,'%') 
        print('Precision:', prec_NWE*100,'%') 
        print('Recall:', recall_NWE*100,'%') 
        print('F-measure:', fmeasure_NWE*100,'%') 
    
   
# Function to display a list of the suggested words
def showSuggestions():
    suggestedWords.delete(0, END)
    options=[]
    word_to_replace = entredSentence.get(tk.SEL_FIRST, tk.SEL_LAST) #to detect the highlighted area  
    index=tokenized_sentence.index(word_to_replace)
    
    candidate_words = get_corrections([tokenized_sentence[index-1]], word_to_replace, vocabulary, n=3, verbose=False)
    print("\nSuitable candidate words are:")
    print('candidate words:', candidate_words)
    for i in range(len(candidate_words)):
        suggestedWords.insert(END,candidate_words[i][0])

    
# Function to replace a misspelled word with the correct word from a list of suggested words            
def replace_word():
    word_to_replace = entredSentence.get(tk.SEL_FIRST, tk.SEL_LAST)   
    selected_word=suggestedWords.get(ANCHOR)
    offset = '+%dc' % len(word_to_replace) # +5c (5 chars)
    idx = '1.0'
    #searches for desried string from index 1  
    idx = outputSentence.search(word_to_replace, idx, nocase = 1,  
                            stopindex = END) 
    # last index sum of current index and  
    # length of text  
    lastidx = '% s+% dc' % (idx, len(word_to_replace)) 
  
    outputSentence.delete(idx, lastidx) 
    outputSentence.insert(idx, selected_word) 
  
    lastidx = '% s+% dc' % (idx, len(selected_word))  

# Function to highlight the listbox from keyword search 
def highlight():
    searchx = SEARCH.get()
    searchx = searchx.lower()
    for i,item in enumerate (all_listbox_item):
        if searchx in item:
            listbox.selection_set(i) #highlights word
            listbox.see(i) #scrolls down to word if not within the listbox
        else:
            listbox.selection_clear(i)
        if searchx == '':
            listbox.selection_clear(0,"end")
            
# Function to clear the text in Searchbox    
def Reset():
    global SEARCH
    clearinput = ""
    SEARCH.set(clearinput)

# Function to enable a pop up window on right click
def do_popup(event): 
	try: 
		m.tk_popup(event.x_root, event.y_root) 
	finally: 
		m.grab_release()    

# when the popup window opens on right click, it will have a word called suggest which will execute the showSuggestions function
m = Menu(root, tearoff = 0) 
m.add_command(label ="suggest", command=showSuggestions) 

SEARCH = StringVar()
# Input widget for sentence to be entred by user
Label(text="Key in sentence here (Not more than 500 words)", fg = "snow", bg = "steel blue", font="Arial 11 bold").place(x=15, y=120)
entredSentence = Text(root, height = 10, width = 60)
entredSentence.configure(font=("Arial", 11))
entredSentence.place(x=15, y=150)
submit_btn = Button(root, height=1, width=10, text="Submit", command=getInput).place(x=575, y=150) 
entredSentence.tag_config("blue_tag", foreground="blue", underline=1) 
entredSentence.tag_config("red_tag", foreground="red", underline=1) 
entredSentence.tag_bind("red_tag", '<Button-3>', do_popup) #calls the pop up funtion
entredSentence.tag_bind("blue_tag", '<Button-3>', do_popup) #calls the pop up funtion

# Creating a suggestions widget for the suggested words to correct the mispelled word
Label(text="Select suggested word for the misspelled word below:", fg = "snow", bg = "steel blue", font = "Arial 11 bold").place(x=15, y=360)
suggestedWords = Listbox(root, height = 10, width = 30)
suggestedWords.configure(font=("Arial", 11))
suggestedWords.place(x=15, y = 390)
replace_btn = Button(root, text="Replace Word", command=replace_word).place(x=305, y=390) 

 
# Output widget for the sentence entered and open for correcting mispelled words
Label(text="User Corrected words as below:", fg = "snow", bg = "steel blue", font = "Arial 11 bold").place(x=15, y=600)
outputSentence = Text(root, height = 10, width = 60, wrap=WORD)
outputSentence.configure(font=("Arial", 11))
#outputSentence.config(state = "disabled")
outputSentence.place(x=15, y=630)


#---------------------------------WIDGETS FOR DICTIONARY-----------------------------------

#=====================================LABEL WIDGET=========================================
lbl_title = Label(root, width=20, font=('arial', 8), text="Dictionary").place(x=550, y=360) 

#=====================================ENTRY WIDGET=========================================
search_entry = Entry(root, textvariable=SEARCH).place(x=550, y=530)

#=====================================BUTTON WIDGET========================================
btn_search = Button(root, text="Search", bg="#006dcc", command=highlight).place(x=550, y=555) 
btn_reset = Button(root=search_entry, text="Reset", bg="#ff0000",command=Reset).place(x=635, y=555) 

#=====================================Table WIDGET=========================================
#highlight the selection in listbox
listbox = Listbox(root, height=9)
selection = listbox.curselection()
listbox.place(x=550,y=380) 

#upload csv to listbox and populate it
with open('econ_corpus.csv', 'r') as f: # change the relative path to csv file path
  reader = csv.reader(f)
  my_list = list(reader)
  for item in my_list:
      listbox.insert("end", item)

all_listbox_item = listbox.get(0, "end")

    


 
# Activating the GUI
root.mainloop()

