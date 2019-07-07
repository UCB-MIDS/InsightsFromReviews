import nltk
import json
import sys
import languageUtils
import time
from tqdm import tqdm
from gensim.summarization import summarize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktLanguageVars


# Loading Data

def loadFromDb(file, count):
    """
    Read count number of lines from the JSON DB into a dictionary
    Count = 0 reads in all the lines

    """

    n = 0
    file_d = []

    with open(file, "r") as f:
        for line in tqdm(f):
            file_d.append(json.loads(line))
            n =  n + 1
            if count > 0 and n == count:
                break
    print(str(len(file_d)) + " Reviews written to the dictionary ")
    return(file_d)


def loadToStringAndClassify(file_d, filter_l = []):
    """
    Consolidate review text into a string
    If there is a list of ASIN's, only pick reviews for those
    Separate reviews into high(pos) and low(neg) ratings

    """

    reviews_str = ""
    reviews_pos_str = ""
    reviews_neg_str = ""

    for r in tqdm(file_d):
        if (len(filter_l) and (r['asin'] in filter_l)) or len(filter_l) == 0:
            # reviews_sent.append(r['reviewText'])
            reviews_str = reviews_str + str(r['reviewText'])
            if ((r['overall'] == 1.0) or (r['overall'] == 2.0)):
                reviews_neg_str = reviews_neg_str + str(r['reviewText'])
            else:
                reviews_pos_str = reviews_pos_str + str(r['reviewText'])

    print(str(len(reviews_str)) + " len reviews string, " + str(len(reviews_pos_str)) + " len Positive reviews string, " + str(len(reviews_neg_str)) + "len Negative reviews string ")
    return reviews_str, reviews_pos_str, reviews_neg_str


# Summarization

def summarizeString(reviews_str, ratio = .5):
    """
    Summarize the text using gensim

    """

    reviews_sum_str = ""
    print(str(len(reviews_str)) + " len input string ")
    reviews_sum_str = summarize(reviews_str, ratio)
    print(str(len(reviews_sum_str)) + " len output string ")
    return reviews_sum_str


def stringToSentences(reviews_str, in_sent_end_chars = ('pros:', 'cons:', '[','][','.','?','!')):
    """
    Break the string into sentences
    Option to give keywords or tokens for separating sentences

    """

    class ReviewLangVars(PunktLanguageVars):
    	sent_end_chars = in_sent_end_chars

    sent_tokenizer1 = PunktSentenceTokenizer(lang_vars = ReviewLangVars())
    sent_review = sent_tokenizer1.tokenize(reviews_str)
    print("Converted to: " + str(len(sent_review)) + " Sentences ")
    return sent_review

def extractFeaturePhrases(sent_pos_review, sent_neg_review, feature_patterns, items):
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

    # Convert to tokens
    pos_sen_tok = []
    neg_sen_tok = []
    neutral_sen_tok = []

    for sentence in tqdm(positive_review):
        pos_sen_tok.append(nltk.word_tokenize(sentence))
    for sentence in tqdm(negative_review):
        neg_sen_tok.append(nltk.word_tokenize(sentence))
    for sentence in tqdm(neutral_review):
        neutral_sen_tok.append(nltk.word_tokenize(sentence))

    print("Tokenized : " + str(len(neutral_sen_tok)) + " neutral sentences")
    print("Tokenized : " + str(len(pos_sen_tok)) + " positive sentences")
    print("Tokenized : " + str(len(neg_sen_tok)) + " negative sentences")

    # Gave an error without downloading the nltk averaged_perceptron_tagger
    # Find POS tags for positive, negative and neutral sentences
    pos_sen_tok_tagged = []
    neg_sen_tok_tagged = []
    neutral_sen_tok_tagged = []

    for sentence_t in tqdm(pos_sen_tok):
        pos_sen_tok_tagged.append(nltk.tag.pos_tag(sentence_t))
    for sentence_t in tqdm(neg_sen_tok):
        neg_sen_tok_tagged.append(nltk.tag.pos_tag(sentence_t))
    for sentence_t in tqdm(neutral_sen_tok):
        neutral_sen_tok_tagged.append(nltk.tag.pos_tag(sentence_t))

    print("POS Tagged : " + str(len(neutral_sen_tok_tagged)) + " neutral sentences")
    print("POS Tagged : " + str(len(pos_sen_tok_tagged)) + " positive sentences")
    print("POS Tagged : " + str(len(neg_sen_tok_tagged)) + " negative sentences")

    # Extract phrases
    extracted_neutral = languageUtils.extractPhrasesFromTagged(neutral_sen_tok_tagged, feature_patterns)
    extracted_pos = languageUtils.extractPhrasesFromTagged(pos_sen_tok_tagged, feature_patterns)
    extracted_neg = languageUtils.extractPhrasesFromTagged(neg_sen_tok_tagged, feature_patterns)

    print("Extraced : " + str(len(extracted_neutral)) + " from neutral sentences")
    print("Extracted : " + str(len(extracted_pos)) + " from positive sentences")
    print("Extracted : " + str(len(extracted_neg)) + " from negative sentences")

    return extracted_neutral, extracted_pos, extracted_neg

# Extract sentences with features
def featuresAndContext(item_arr, opinion_phrases, sentence_arr ):
    """ Extract sentences with features/opinion_phrases
    item_arr is to constrain the context to items under study
    Output is extracted into a file
    """

    count = 0
    # Latest time in a string
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # Outputfile
    print("File created at: " + timestr)
    output_file_name = "o_" + timestr + ".txt"
    f= open(output_file_name,"a+")
    # Go through the phrases and print sentences that contain them
    for phrase, freq in sorted(opinion_phrases, key = lambda phrase_freq: phrase_freq[1], reverse = True):
        # Count of the number of sentences
        pcount = 0
        count+=1
        f.write("\r\n")
        f.write("---" + "Phrase > " + str(count) + " >>> " + phrase + "----\r\n\r\n")
        for l in sentence_arr:
            if languageUtils.normalise(phrase) in languageUtils.normalise(l):
                pcount+=1
                f.write("---" + "example > " + str(pcount) + " >>> " + "----\r\n")
                f.write("%s\r\n" %(l))
                if pcount==4:
                    break
        if count==4:
            break
    return output_file_name
    f.close()
