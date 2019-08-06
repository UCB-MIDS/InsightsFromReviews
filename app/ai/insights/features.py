import nltk
import json
import sys
from . import languageUtils
import time
from tqdm import tqdm
from gensim.summarization import summarize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktLanguageVars
from collections import defaultdict

# Loading Data

def loadFromDb(file, count = 0, filter_l = ""):
    """
    Read count number of lines from the JSON DB into a dictionary
    Count = 0 reads in all the lines

    """

    n = 0
    file_d = []

    with open(file, "r") as f:
        for line in tqdm(f):
            line = json.loads(line)
            if (filter_l and (line['asin'] == filter_l)) or not filter_l:
                file_d.append(line)
                n =  n + 1
            if count > 0 and n == count:
                break
    print(str(len(file_d)) + " Reviews written to the dictionary ")
    return(file_d)


def loadFromJsonString(js, count = 0):
    """
    Read count number of lines from the JSON string into a dictionary
    Count = 0 reads in all the lines
    JS is already a list of strings, so the function was modified to just be a passthrough

    """
    print(str(len(js)) + " Reviews written to the dictionary ")
    return(js)


def loadTolistsAndClassify(file_d, filter_l = "", count = 0):
    """
    Consolidate review text into a list
    If there is a filter (asin) only pick up count reviews for that asin
    Separate reviews into high(pos) and low(neg) ratings

    """

    n = 0
    reviews_sent = []
    reviews_neg_sent = []
    reviews_pos_sent = []

    for r in tqdm(file_d):
        if (filter_l and (r['asin'] == filter_l)) or not filter_l:
            if r['reviewText'] not in reviews_sent:
                reviews_sent.append(r['reviewText'])
            if ((r['overall'] == 1.0) or (r['overall'] == 2.0)):
                if r['reviewText'] not in reviews_neg_sent:
                    reviews_neg_sent.append(r['reviewText'])
            else:
                if r['reviewText'] not in reviews_pos_sent:
                    reviews_pos_sent.append(r['reviewText'])

            n = n+1
            if count > 0 and n == count:
                break

    print("Processed and Classified " + str(n) + " Reviews")
    print(str(len(reviews_pos_sent)) + " Positive reviews")
    print(str(len(reviews_neg_sent)) + " Negative reviews")
    return reviews_sent, reviews_pos_sent, reviews_neg_sent

def loadToString(reviews_sent):
    """
    Consolidate review text into a string
    """

    # reviews_str = "".join(s for s in reviews_sent)
    # Space among the joined reviews to help with sentence boundaries
    reviews_str = " ".join(s for s in reviews_sent)
    print("Converted " + str(len(reviews_str)) + " len reviews string")
    return reviews_str


# Summarization

def summarizeString(reviews_str, ratio = 0.5):
    """
    Summarize the text using gensim

    """

    reviews_sum_str = ""
    print(str(len(reviews_str)) + " len input string ")
    reviews_sum_str = summarize(reviews_str, ratio)
    print(str(len(reviews_sum_str)) + " len summarized string ")
    return reviews_sum_str


def stringToSentences(reviews_str, in_sent_end_chars = ('pros:', 'cons:', '[','][','.','?','!', ']')):
    """
    Break the string into sentences
    Option to give keywords or tokens for separating sentences

    """

    class ReviewLangVars(PunktLanguageVars):
    	sent_end_chars = in_sent_end_chars

    sent_tokenizer1 = PunktSentenceTokenizer(lang_vars = ReviewLangVars())
    # sent_tokenizer2 = PunktSentenceTokenizer()
    sent_review = sent_tokenizer1.tokenize(reviews_str)
    print("Converted to: " + str(len(sent_review)) + " Sentences ")
    return sent_review

def extractFeaturePhrases(sent_pos_review, sent_neg_review, feature_patterns, items):
    """ Take a list of Sentences
    tokenize
    POS
    Extract phrases that match a pattern
    """

    positive_review=[]
    negative_review=[]
    neutral_review=[]

    # Extracting sentiments from the positive reviews
    for sentence in tqdm(sent_pos_review):
        #print(i[0][0] +"--" + sentence)
        sentence = languageUtils.clean(sentence)
        # Crashes
        # sentence = languageUtils.replacePronouns(sentence)
        # for i in items:
        #     if i[0][0] in sentence:
        x=languageUtils.getPolarity(sentence)
        if(x=="pos"):
            positive_review.append(sentence)
        elif(x=="neg"):
            negative_review.append(sentence)
        else:
            neutral_review.append(sentence)
            # positive_review.append(sentence)
                # break

    # Extracting sentiments from the negative reviews
    for sentence in tqdm(sent_neg_review):
        #print(i[0][0] +"--" + sentence)
        sentence = languageUtils.clean(sentence)
        # Crashes
        # sentence = languageUtils.replacePronouns(sentence)
        # for i in items:
        #     if i[0][0] in sentence:
        x=languageUtils.getPolarity(sentence)
        if(x=="pos"):
            positive_review.append(sentence)
        elif(x=="neg"):
            negative_review.append(sentence)
        else:
            # negative_review.append(sentence)
            neutral_review.append(sentence)
                # break

    print("Extracted : " + str(len(positive_review)) + " positive sentences")
    # print(positive_review)
    print("Extracted : " + str(len(negative_review)) + " negative sentences")
    # print(negative_review)

    # Convert to tokens
    pos_sen_tok = []
    neg_sen_tok = []

    for sentence in tqdm(positive_review):
        pos_sen_tok.append(nltk.word_tokenize(sentence))
    for sentence in tqdm(negative_review):
        neg_sen_tok.append(nltk.word_tokenize(sentence))

    print("Tokenized : " + str(len(pos_sen_tok)) + " positive sentences")
    print("Tokenized : " + str(len(neg_sen_tok)) + " negative sentences")

    # Gave an error without downloading the nltk averaged_perceptron_tagger
    # Find POS tags for positive, negative and neutral sentences
    pos_sen_tok_tagged = []
    neg_sen_tok_tagged = []

    for sentence_t in tqdm(pos_sen_tok):
        pos_sen_tok_tagged.append(nltk.tag.pos_tag(sentence_t))
    for sentence_t in tqdm(neg_sen_tok):
        neg_sen_tok_tagged.append(nltk.tag.pos_tag(sentence_t))

    print("POS Tagged : " + str(len(pos_sen_tok_tagged)) + " positive sentences")
    print("POS Tagged : " + str(len(neg_sen_tok_tagged)) + " negative sentences")

    # Extract phrases
    extracted_pos = languageUtils.extractPhrasesFromTagged(pos_sen_tok_tagged, feature_patterns)
    extracted_neg = languageUtils.extractPhrasesFromTagged(neg_sen_tok_tagged, feature_patterns)

    print("Extracted : " + str(len(extracted_pos)) + " phrases from positive sentences")
    print("Extracted : " + str(len(extracted_neg)) + " phrases from negative sentences")

    return extracted_pos, extracted_neg


def extractFeaturePhrasesStrict(sent_pos_review, sent_neg_review, feature_patterns, items):
    """ Take a list of Sentences
    tokenize
    POS
    Extract phrases that match a pattern
    """

    neutral_review=[]
    positive_review=[]
    negative_review=[]

    # Extracting sentiments from the positive reviews
    for sentence in tqdm(sent_pos_review):
        sentence = languageUtils.clean(sentence)
        for i in items:
            if i[0][0] in sentence:
                #print(i[0][0] +"--" + sentence)
                x=languageUtils.getPolarity(sentence)
                if(x=="pos"):
                    positive_review.append(sentence)
                elif(x=="neg"):
                    negative_review.append(sentence)
                else:
                    neutral_review.append(sentence)
                break

    # Extracting sentiments from the negative reviews
    for sentence in tqdm(sent_neg_review):
        sentence = languageUtils.clean(sentence)
        for i in items:
            if i[0][0] in sentence:
                #print(i[0][0] +"--" + sentence)
                x=languageUtils.getPolarity(sentence)
                if(x=="pos"):
                    positive_review.append(sentence)
                elif(x=="neg"):
                    negative_review.append(sentence)
                else:
                    neutral_review.append(sentence)
                break

    print("Extracted : " + str(len(neutral_review)) + " neutral sentences")
    print("Extracted : " + str(len(positive_review)) + " positive sentences")
    print("Extracted : " + str(len(negative_review)) + " negative sentences")

    # Time to remove all the stop words
    # Before tokenization

    neutral_review_clean = []
    for sentence in tqdm(neutral_review):
        neutral_review_clean.append(languageUtils.clean(sentence, remove_stopwords=True))

    positive_review_clean = []
    for sentence in tqdm(positive_review):
        positive_review_clean.append(languageUtils.clean(sentence, remove_stopwords=True))

    negative_review_clean = []
    for sentence in tqdm(negative_review):
        negative_review_clean.append(languageUtils.clean(sentence, remove_stopwords=True))

    print("Cleaned : " + str(len(neutral_review_clean)) + " neutral sentences")
    print("Cleaned : " + str(len(positive_review_clean)) + " positive sentences")
    print("Cleaned : " + str(len(negative_review_clean)) + " negative sentences")

    # Convert to tokens
    pos_sen_tok = []
    neg_sen_tok = []
    neutral_sen_tok = []

    for sentence in tqdm(neutral_review_clean):
        neutral_sen_tok.append(nltk.word_tokenize(sentence))
    for sentence in tqdm(positive_review_clean):
        pos_sen_tok.append(nltk.word_tokenize(sentence))
    for sentence in tqdm(negative_review_clean):
        neg_sen_tok.append(nltk.word_tokenize(sentence))

    print("Tokenized : " + str(len(neutral_sen_tok)) + " neutral sentences")
    print("Tokenized : " + str(len(pos_sen_tok)) + " positive sentences")
    print("Tokenized : " + str(len(neg_sen_tok)) + " negative sentences")

    # Gave an error without downloading the nltk averaged_perceptron_tagger
    # Find POS tags for positive, negative and neutral sentences
    pos_sen_tok_tagged = []
    neg_sen_tok_tagged = []
    neutral_sen_tok_tagged = []

    for sentence_t in tqdm(neutral_sen_tok):
        neutral_sen_tok_tagged.append(nltk.tag.pos_tag(sentence_t))
    for sentence_t in tqdm(pos_sen_tok):
        pos_sen_tok_tagged.append(nltk.tag.pos_tag(sentence_t))
    for sentence_t in tqdm(neg_sen_tok):
        neg_sen_tok_tagged.append(nltk.tag.pos_tag(sentence_t))

    print("POS Tagged : " + str(len(neutral_sen_tok_tagged)) + " neutral sentences")
    print("POS Tagged : " + str(len(pos_sen_tok_tagged)) + " positive sentences")
    print("POS Tagged : " + str(len(neg_sen_tok_tagged)) + " negative sentences")

    # Extract phrases
    extracted_neutral = languageUtils.extractPhrasesFromTagged(neutral_sen_tok_tagged, feature_patterns)
    extracted_pos = languageUtils.extractPhrasesFromTagged(pos_sen_tok_tagged, feature_patterns)
    extracted_neg = languageUtils.extractPhrasesFromTagged(neg_sen_tok_tagged, feature_patterns)

    print("Extracted : " + str(len(extracted_neutral)) + " phrases from neutral sentences")
    print("Extracted : " + str(len(extracted_pos)) + " phrases from positive sentences")
    print("Extracted : " + str(len(extracted_neg)) + " phrases from negative sentences")

    return extracted_neutral, extracted_pos, extracted_neg

# Extract sentences with features
def featuresAndContext(item_arr, opinion_phrases, sentence_arr, phrase_count, sentence_count ):
    """ Extract sentences with features/opinion_phrases
    item_arr is to constrain the context to items under study
    Output is returned as a JSON string
    """

    # Output JSON
    outDict = defaultdict(list)
    outJSON = ''

    # Also creating a summary strings

    p_count = 0
    # Go through the phrases and print sentences that contain them
    # for phrase, freq in sorted(opinion_phrases, key = lambda phrase_freq: phrase_freq[1], reverse = True):
    for phrase, freq in opinion_phrases:
        # f.write("\r\n")
        # f.write("---" + "Phrase > " + str(p_count) + " >>> " + phrase + "----\r\n\r\n")
        p_count += 1
        s_count = 0
        # summary = ''
        for l in sentence_arr:
            if languageUtils.normalise(phrase) in languageUtils.normalise(languageUtils.clean(l, remove_stopwords=True)):
                # f.write("---" + "example > " + str(s_count) + " >>> " + "----\r\n")
                # f.write("%s\r\n" %(l))
                outDict[phrase].append(l)
                s_count += 1
                if s_count == sentence_count:
                    break
        # summary = " ".join(s for s in outDict[phrase])
        # print(summary)
        # summary = summarizeString(summary, ratio = .4)
        # print(summary)
        # summary = languageUtils.extractSubjective(summary)
        # print(summary)
        if p_count == phrase_count:
            break
    outJSON = json.dumps(outDict, sort_keys = False, indent = 4)
    # with open(output_json_name, 'w') as jf:
        # json.dump(outDict, jf, sort_keys = True, indent=4)

    # f.close()
    return outJSON
