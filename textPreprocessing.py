import os
import bs4 as bs
# import beautifulsoup4 as bs
import requests
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import re


print('DEPENDENCIES INSTALLED')
# 
stopL=[]
for filename in os.listdir(r'StopWords'):
    f = os.path.join(r'StopWords', filename)
    # checking if it is a file
    if os.path.isfile(f):
        stopL.append(f)

stopWords=[]
for path in stopL:
    file1 = open(path, 'r')
    Lines = file1.readlines()

    print()
    count = 0
    # Strips the newline character
    for line in Lines:
        count += 1
        # print("Line {}: {}".format(count, line.strip().split()[0] ))
        stopWords.append(line.strip().split()[0] )
    # print('*'*75)

print(f'Stop Words extracted from the path...')

with open(r'MasterDictionary\positive-words.txt','r') as f:
    pos = f.readlines()
    pos = [x.replace('\n','') for x in pos]
    pos = [x for x in pos if x not in stopWords] 

with open(r'MasterDictionary\negative-words.txt','r') as f:
    neg = f.readlines()
    neg = [x.replace('\n','') for x in neg]
    neg = [x for x in neg if x not in stopWords] 

print('Positive and Negative words extracted from their designated paths...')

print('Now reading text from the websites...')

df=pd.read_excel('Input.xlsx')

print('Excel file is ready')

headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}

rawCorp=[]
listCorp=[]
lemmatizer=WordNetLemmatizer()
for ind,url in enumerate(df['URL']):
    
    r = requests.get(url,headers=headers)
    if r.status_code == 404:
        print(f'URL {url} of index {ind} does not exist, error 404')
        listCorp.append(' ')
        rawCorp.append(' ')
        continue
    else:
        print(f'Scraping Text from {url} of index {ind}')
    
    # soup = bs.BeautifulSoup(r.content,'lxml')
    # lxml parser not functionable
    soup = bs.BeautifulSoup(r.content,'html.parser')
    raw=''
    corpus=''
    
    for para in soup.find_all('p',class_=''):
        for word in word_tokenize(para.text):
            raw = raw +' '+ word.lower()
            if word not in stopWords:
                rev=re.sub("[^a-zA-Z0-9\']",' ',word)
                rev=rev.lower()
                rev=lemmatizer.lemmatize(rev)
                corpus=corpus+' '+rev
    listCorp.append(corpus)
    rawCorp.append(raw)

df['CleanedCorpus']=listCorp
df['RawCorpus']=rawCorp

print('Calculating the Positive Scores, Negative Scores, Subjectivity and Polarity of the websites...')

posL=[]
negL=[]
polL=[]
subL=[]
for corp in df['CleanedCorpus']:
    posScore=0
    negScore=0
    for word in word_tokenize(corp):
        if word in pos:
            posScore+=1
        if word in neg:
            negScore+=1

    polarityScore = (posScore-negScore)/((posScore+negScore)+0.000001)
    subjectivityScore = (posScore+negScore)/((len(word_tokenize(corpus))) + 0.000001)
    posL.append(posScore)
    negL.append(negScore)
    polL.append(polarityScore)
    subL.append(subjectivityScore)

df['PositiveScore']=posL
df['NegativeScore']=negL
df['PolarityScore']=polL
df['SubjectivityScore']=subL

print('Calculating the number of complex words and average sentence length...')
avgSenLen=[]
complexCount=[]
senLength=[]
wordLength=[]
for corp in df['RawCorpus']:
    senLen=len(sent_tokenize(corp))
    senLength.append(senLen)
    
    wordLen=len(word_tokenize(corp))
    wordLength.append(wordLen)
    
    if senLen==0:
        avgSenLen.append(0)
    else:
        avgSenLen.append(wordLen/senLen)
    
    cmplx = 0
    for myword in word_tokenize(corp):
        d = {}.fromkeys('aeiou',0)
        haslotsvowels = False
        for x in myword.lower():
            if x in d:
                d[x] += 1
        for q in d.values():
            if q > 2:
                haslotsvowels = True
        if haslotsvowels:
            cmplx += 1
    complexCount.append(cmplx)
        
df['RawSenCount']=senLength
df['RawWordCount']=wordLength
df['avgSenLen']=avgSenLen
df['complexCount']=complexCount

print('Calculating the Gunning Fog Index...')
df['Fog Index']=0.4*(df['avgSenLen']+(100*df['complexCount']/df['RawWordCount']))

cleanWordCount=[]
for corp in df['CleanedCorpus']:
    cleanWordCount.append(len(word_tokenize(corp)))
df['cleanWordCount']=cleanWordCount

print('Counting the number of syllables...')
def stem(word):
    for suffix in ['ed','es']:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

syllables=[]
for corp in df['CleanedCorpus']:
    sylCount=0
    for word in word_tokenize(corp):
        tempo=stem(word) # Stems the word if it has not already been lemmatized
        d = {}.fromkeys('aeiou',0)
        for x in tempo:
            if x in d:
                d[x] += 1
        sylCount+=sum(d.values())
    syllables.append(sylCount)
df['syllables']=syllables

print('Calculating Personal Pronouns...')
personalPronouns=[]
for corp in df['RawCorpus']:
    totPron=0
    for pron in ["i","we","my","ours","us"]:
        re_pron = r"\b{}\b".format(pron)
        count_pron = len(re.findall(re_pron, corp))
        totPron+=count_pron
    personalPronouns.append(totPron)
df['PersonalPronouns']=personalPronouns

print('Calculating Characters...')

charCount=[]
for corp in df['RawCorpus']:
    charCount.append(len(corp.replace(' ','')))
df['charCount']=charCount
df['AvgWordLen']=df['charCount']/df['RawWordCount']

print('Ammending Erratas from 404 websites...')
### Fixing any 0 or None or NAN or INF value errors from 404 websites
df.fillna(0,inplace=True)
df.replace([np.inf, -np.inf], 0, inplace=True)

print('Compiling the information in the Output Data Structure.xlsx file')

### Compiling the entire info into 
data=pd.read_excel('Output Data Structure.xlsx')

data['POSITIVE SCORE']=df['PositiveScore']
data['NEGATIVE SCORE']=df['NegativeScore']
data['POLARITY SCORE']=df['PolarityScore']
data['SUBJECTIVITY SCORE']=df['SubjectivityScore']
data['AVG SENTENCE LENGTH']=df['avgSenLen'] ## I feel this was supposed to be in character length, but followed the assignment's instructions
data['PERCENTAGE OF COMPLEX WORDS']=100*df['complexCount']/df['RawWordCount']
data['FOG INDEX']=df['Fog Index']
data['AVG NUMBER OF WORDS PER SENTENCE']=df['avgSenLen']
data['COMPLEX WORD COUNT']=df['complexCount']
data['WORD COUNT']=df['cleanWordCount']
data['SYLLABLE PER WORD']=df['syllables']/df['RawWordCount']
data['PERSONAL PRONOUNS']=df['PersonalPronouns']
data['AVG WORD LENGTH']=df['AvgWordLen']

print('Saving... Preprocessed.csv and Overwriting Output Data Structure.xlsx...')

df.to_csv('Preprocessed.csv',index=False)
data.to_excel('Output Data Structure.xlsx',index=False)

print('...End of Program, pls hire me...')