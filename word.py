
import re

lists = list()

with open("econ_corpus_THC.txt", "r", encoding = 'ISO-8859-1') as fin:
    data = fin.read()
data = re.sub(r'[^A-Za-z\.\?!\']+', ' ', data) #remove special character
data = re.sub(r'[A-Z]{3,}[a-z]+', ' ',data) #remove words with more than 3 Capital letters
sentences = re.split(r'[\.\?!]+[ \n]+', data) #split data into sentences
sentences = [s.strip() for s in sentences] #Remove leading & trailing spaces
sentences = [s for s in sentences if len(s) > 0] #Remove whitespace
for line in sentences:
    for word in line.split():
        lists.append(word.strip())
          
#sort the corpus
gx =lists.sort()
#print(lists)

#remove duplicate word
#nodupe = []
#for dupe in lists:
#    if dupe not in nodupe:
#        nodupe.append(dupe)
#print(nodupe)
from collections import Counter

def remov_duplicates(lists): 

    for i in range(0, len(gx)): 
            gx[i] = "".join(gx[i]) 
        
  
    # now create dictionary using counter method 
    # which will have strings as key and their  
    # frequencies as value 
    UniqW = Counter(gx) 
  
    # joins two adjacent elements in iterable way 
    s = " ".join(UniqW.keys()) 

    return (s)

nodupe = remov_duplicates(gx)

#saving the sorted and clean corpus word in csv
filename = 'econcorpusTHC.csv' #change this filename
with open(filename,'w') as fout:
     for clean in nodupe:
         fout.write(clean + '\n')


