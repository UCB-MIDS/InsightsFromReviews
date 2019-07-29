import sys
import nltk
import re
from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser
from nltk.corpus import stopwords
from nltk.corpus import opinion_lexicon
from nltk.tokenize import treebank
from tqdm import tqdm
import inflect
import spacy # version 2.1.3
import neuralcoref # version 4.0
from textblob import TextBlob

'''
Prerequisites
nltk.download('averaged_perceptron_tagger')
nltk.download('opinion_lexicon')
python -m spacy download en_core_web_sm
nltk.download('stopwords')
'''

# A list of contractions from http://stackoverflow.com/questions/19790188/expanding-english-language-contractions-in-python
contractions = {
"ain't": "am not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he would",
"he'd've": "he would have",
"he'll": "he will",
"he's": "he is",
"how'd": "how did",
"how'll": "how will",
"how's": "how is",
"i'd": "i would",
"i'll": "i will",
"i'm": "i am",
"i've": "i have",
"isn't": "is not",
"it'd": "it would",
"it'll": "it will",
"it's": "it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"must've": "must have",
"mustn't": "must not",
"needn't": "need not",
"oughtn't": "ought not",
"shan't": "shall not",
"sha'n't": "shall not",
"she'd": "she would",
"she'll": "she will",
"she's": "she is",
"should've": "should have",
"shouldn't": "should not",
"that'd": "that would",
"that's": "that is",
"there'd": "there had",
"there's": "there is",
"they'd": "they would",
"they'll": "they will",
"they're": "they are",
"they've": "they have",
"wasn't": "was not",
"we'd": "we would",
"we'll": "we will",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what will",
"what're": "what are",
"what's": "what is",
"what've": "what have",
"where'd": "where did",
"where's": "where is",
"who'll": "who will",
"who's": "who is",
"won't": "will not",
"wouldn't": "would not",
"you'd": "you would",
"you'll": "you will",
"you're": "you are"
}


# Extracting key nouns from the text
# This is to make sure that the features are somewhat connected to the item/ASIN under study

def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
    """calculates the support for items in the itemSet and returns a subset
   of the itemSet each of whose elements satisfies the minimum support"""
    _itemSet = set()
    localSet = defaultdict(int)

    for item in itemSet:
            for transaction in transactionList:
                    if item.issubset(transaction):
                            freqSet[item] += 1
                            localSet[item] += 1

    for item, count in localSet.items():
            support = float(count)/len(transactionList)

            if support >= minSupport:
                    _itemSet.add(item)

    return _itemSet


def joinSet(itemSet, length):
    """Join a set with itself and returns the n-element itemsets"""
    return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])


def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    return itemSet, transactionList


def runApriori(data_iter, minSupport, minConfidence):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport

    assocRules = dict()
    # Dictionary which stores Association Rules

    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet,
                                                transactionList,
                                                minSupport,
                                                freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
            """local function which Returns the support of an item"""
            return float(freqSet[item])/len(transactionList)

    toRetItems = []
    for key, value in tqdm(list(largeSet.items())):
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])

    toRetRules = []
    for key, value in tqdm(list(largeSet.items())[1:]):
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0:
                    confidence = getSupport(item)/getSupport(element)
                    if confidence >= minConfidence:
                        toRetRules.append(((tuple(element), tuple(remain)),
                                           confidence))
    return toRetItems, toRetRules


def printAprioriResults(items):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    for item, support in sorted(items, key=lambda item_support: item_support[1], reverse=True):
        print(str(item), support)

# Utility functions


stop_words = stopwords.words('english')
# Map between the lemma and the actual word
lem_word_mapping = {}

# Find leaves of a tree
def leaves(tree):
    """Finds leaf nodes of a chunk tree."""
    for subtree in tree.subtrees(filter = lambda t: t.label() in ['P1','P2','P3','P4','P5','P6','P7','P8']):
        yield subtree.leaves()

def stem(word):
    """Normalises words to lowercase and stems and lemmatizes it."""
    stemmer = nltk.stem.porter.PorterStemmer()
    word = word.lower()
    word = word.replace("'","").replace('"','').replace('.','')
    word1 = stemmer.stem(word)
    return word1

# lowercase, stem and lemmatize
def normalise(word):
    """Normalises words to lowercase and stems and lemmatizes it."""
    stemmer = nltk.stem.porter.PorterStemmer()
    lem = nltk.WordNetLemmatizer()
    word = word.lower()
    word1 = stemmer.stem(word)
    word2 = lem.lemmatize(word1)
    if word != word2:
        lem_word_mapping[word2] = word
    return word2


def clean(text, remove_stopwords = False):
    '''Remove unwanted characters, stopwords, and format the text to create fewer nulls'''

    # Convert words to lower case
    text = text.lower()

    # Replace contractions with their longer forms
    text = text.split()
    new_text = []
    for word in text:
        if word in contractions:
            new_text.append(contractions[word])
        else:
            new_text.append(word)
    text = " ".join(new_text)

    # Format words and remove unwanted characters
    text = re.sub(r'https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\<a href', ' ', text)
    text = re.sub(r'&amp;', '', text)
    text = re.sub(r'["\-;%()|+&=*%.,!?:#$@\[\]/]', ' ', text)
    text = re.sub(r'<br />', ' ', text)
    text = re.sub(r'\'', ' ', text)

    # Optionally, remove stop words
    if remove_stopwords:
        text = text.split()
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
        text = " ".join(text)

    return text

def acceptableWord(word):
    """Checks conditions for acceptable word: length, stopword."""
    accepted = bool((2 <= len(word) <= 40) and word.lower() not in stop_words)
    return accepted

# extract words after normalizing and checking if acceptable
def getTerms(tree):
    """Returns the words after checking acceptable conditions, normalizing and lemmatizing"""
    term = [ stem(w) for w in tree if acceptableWord(w) ]
    return term

def getTerms1(tree):
    """Returns the words after checking acceptable conditions, normalizing and lemmatizing"""
    term = [ normalise(w) for w in tree if acceptable_word(w) ]
    yield term

def getNorm(tree):
    """Parse leaves in chunk and return after checking acceptable conditions, normalizing and lemmatizing"""
    for leaf in leaves(tree):
        term = [ normalise(w) for w,t in leaf if acceptableWord(w) ]
        yield term

def isNoun(n):
    if n=='NN' or n=='NNS' or n=='NNP' or n=='NNPS':
        return True

def getNouns(sent_review):
    """ Get all acceptable noun stems from the text """
    revset=[]
    for line in tqdm(sent_review):
        # print(line)
        a = nltk.word_tokenize(line)
        # print(a)
        nouns = [word for (word, pos) in nltk.pos_tag(a) if isNoun(pos)]
        # print(nouns)
        terms = getTerms(nouns)
        # print(terms)

        revset.append(terms)
    print("Found " + str(len(revset)) + " Nouns")
    return revset

# Top list of items referred to in the reviews
def getItems(sent_review, minSupport = .1, minConfidence=.1):
    """ Get the most relevant nouns/items from the reviewText
        Assumption is that these items are the subject of the conversation
    """

    revset = getNouns(sent_review)
    items, rules = runApriori(revset, minSupport, minConfidence)
    return items, rules

# Polarity

def getPolarity(sentence):
    """
    Polarity of the sentences, conventional Liu and Hu Opinion Lexicon
    Takes in a sentence and returns the sentiment of the sentence by counting the no of positive and negitive
    and negitive words and by reversing the sentiment if the words NO or NOT are present
    """
    tokenizer = treebank.TreebankWordTokenizer()
    pos_words = 0
    neg_words = 0
    tokenized_sent = [word.lower() for word in tokenizer.tokenize(sentence)]

    x = list(range(len(tokenized_sent)))
    y = []
    isNegation = False
    negationWords = ['no','not','never','none','hardly','rarely','scarcely','']

    for word in tokenized_sent:
        if word in opinion_lexicon.positive():
            pos_words += 1
            y.append(1) # positive
        elif word in opinion_lexicon.negative():
            neg_words += 1
            y.append(-1) # negative
        else:
            y.append(0) # neutral

        if word in negationWords:
            isNegation = True

    if pos_words > neg_words and isNegation==True:
        return 'neg'
    elif pos_words > neg_words:
        return 'pos'
    elif pos_words < neg_words and isNegation==True:
        return 'pos'
    elif pos_words < neg_words:
        return 'neg'
    elif pos_words == neg_words:
        return 'neutral'


def downloadOpinionLexicon():
    """ Download the NLTK opinion Lexicon """
    nltk.download('opinion_lexicon')

def downloadPerceptronTagger():
    """ Download the perceptron tagger """
    nltk.download('averaged_perceptron_tagger')


def sentenceTokenize(reviews):
    """ convert sentences to token/words"""
    sent_tok = []
    for sentence in tqdm(reviews):
        sent_tok.append(nltk.word_tokenize(sentence))
    return sent_tok

def tagTokens(tokens):
    """ convert sentences to token/words"""
    sent_tok_tag = []
    for sentence in tqdm(tokens):
        sent_tok_tag.append(nltk.tag.pos_tag(sentence))

    return sent_tok_tag


# Extracting features

def extractPhrasesFromTagged(tagged, feature_patterns):
    """ Given tagged sentences, extract features with ngram rules """
    out = []
    for phrase in tqdm(tagged):
        r_parser = nltk.RegexpParser(feature_patterns)
        # r_parser = nltk.RegexpParser(grammar)
        chunk_2 = r_parser.parse(phrase)
        term = getNorm(chunk_2)

        for ter in term:
            word_concat = ""
            for word in ter:
                word_concat = word_concat + " " + word

            if (len(ter) > 1):
                out.append(word_concat)

    return out


def getRealWords(phrases):
    """ Unlemmatize and unstem using the dictionary created earlier """
    p = inflect.engine()
    new_phrases=[]
    for a in tqdm(phrases):
        newword="";
        found=False;
        for b in a[0].split():
            for x in lem_word_mapping:
                #print(x)
                #print(b)
                if b==x:
                    found=True
                    sing=(lem_word_mapping[x] if p.singular_noun(lem_word_mapping[x])==False else p.singular_noun(lem_word_mapping[x]))
                    if newword=="":
                        newword = newword + sing
                    else:
                        newword = newword + " " +  sing
            if found==False:
                if newword=="":
                    newword = newword + b
                else:
                    newword = newword + " " +  b
                    #print(newword)
        new_phrases.append((newword,a[1]))
    return new_phrases

def extractSubjective(review):
    """
    Input: entire review document (str)
    Output: shortened review document with only subjective sentences
    """
    sent_list = nltk.sent_tokenize(review)
    output = ""  # output string
    for sent in sent_list:
        result = TextBlob(sent)
        if result.sentiment[1] > 0.30:  # keep sentences with sentiment > 0.25
            output += sent+"  "
    return output


# spacy
def replacePronouns(review):
    """
    Input: entire review document (str), multiple sentence_scores
    Output: string, modified review with pronouns replaced.
    """

    # create spacy model
    nlp = spacy.load('en_core_web_sm')
    # add neuralcoref to spacy model
    neuralcoref.add_to_pipe(nlp, greedyness=0.50, max_dist=75)

    pn = nlp(review)  # pn = pronoun doc
    # print("has coreferences?  {}".format(pn._.has_coref))
    # print("Coreferences:")
    # print(pn._.coref_clusters)

    return pn._.coref_resolved
