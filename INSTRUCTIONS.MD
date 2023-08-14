## Inputs
- Stop Words
- Positive Words
- Negative Words

## Scraping
- used requests and BeautifoulSoup modules for crawling through the websites
- posed a header for User-Agent incase necessary
- Saw a common pattern among all the websites where all the meaningful text had ('p',class_='') the following state
- made two separate columns in a temporary pandas dataFrame
    1. RawCorpus: lowering the text scraped
    2. CleanedCorpus: lowered the text + removed stop words + used regex to only include alphanumeric + removed stop Words + applied Lemmatizer for stemming

## ScorePreprocessing by observing occurence in CleanedCorpus
- POSITIVE SCORE
- NEGATIVE SCORE
- POLARITY SCORE
- SUBJECTIVITY SCORE

## Count of Sentences, Words and Average Word Length and Fog Index
- using the nltk module's word_tokenize() and sent_tokenize() the above were calculated
- Also to note the corpus used is ran through the RawCorpus
- Fog index was calculated using the Gunning Fog Index's Formula stated in the assignment (Objective.docx)

## CleanWordCount and CleanSentenceCount
- Same process is repeated as above with the only change of iterating through CleanedCorpus

## Complex Words
- Any word having more than two syllables is regarded as complex, stemming was also done by creating a custom stemmer method from scratch to remove words ending in "-ed" and "-es"
- I suggest more stemming could be done using more suffixes such as ['ing', 'ly', 'ed', 'ious', 'ies', 'ive', 'es', 's', 'ment']

## Personal Pronouns
- using the regex module's findall method, personal pronouns were calculated in the RawCorpus

## Character Count and Average Word Length
- to find the number of characters in all the words, whitespace is removed dynamically on RawCorpus
- implementing the len() method character count is found
- Average Word Length is calculated by averaging the character count over the number of words from RawCorpus

## Fixing any  None or NAN or INF value errors from 404 websites
- all the errors are replaced by imputing 0

## Finishing
- Output Data Structure.xlsx is imported and values of the DataFrame are filled from the temporary dataset created through the code
