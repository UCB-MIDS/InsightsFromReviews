from . import languageUtils
from . import features
from tqdm import tqdm
import nltk
import sys
import getopt
import json
import time
# from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# import pandas as pd
from pprint import pprint

# This implements the NLP pipeline

def main(argv):

    # Usage
    try:
      opts, args = getopt.getopt(argv,"hi:j:a:c:",["dbfile=", "jsonString=", "asin=", "count="])
    except getopt.GetoptError:
      print ('insights.py -i <dbfile> -j <jsonString> -a <asin> -c <count>')
      sys.exit(2)

    # File with the reviews DB
    file = ""
    js = ""
    asin = ""
    count = 0
    count_a = 0
    # Strings with reviews
    reviews_str = ""
    reviews_pos_str = ""
    reviews_neg_str = ""

    for opt, arg in opts:
        if opt == '-h':
             print ('insights.py -i <dbfile> -j <jsonString> -a <asin>')
             sys.exit()
        elif opt in ("-i", "--dbfile"):
             file = arg
        elif opt in ("-j", "--jsonString"):
             js = arg
        elif opt in ("-a", "--asin"):
             asin = arg
        elif opt in ("-c", "--count"):
             count = int(arg)

    # ASIN corresponding to the Iron Skillet
    # asin = ['B00006JSUA']

    # if asin and count, we load all reviews from the DB and filter while creating a string
    if asin and count:
        count_a = count
        count = 0

    # Load reviews to a dictionary
    if file:
        print('loading reviews from: ' + file)
        file_d = features.loadFromDb(file, count)
        # print(len(file_d))
        # print(file_d[0])
    elif js:
        print('loading reviews from the JSON String')
        file_d = features.loadFromJsonString(js, count)
        # print(len(file_d))
        # print(file_d[0])
    else:
        file = '/Users/gkhanna/Downloads/reviews_Home_and_Kitchen_5.json'
        print('loading reviews from: ' + file)
        file_d = features.loadFromDb(file, count)
        # print(len(file_d))
        # print(file_d[0])

    # Extract all reviews into lists
    reviews_sent, reviews_pos_sent, reviews_neg_sent = features.loadTolistsAndClassify(file_d, filter_l = asin,
    count = count_a )
    # print(len(reviews_str))

    # Convert to strings
    reviews_str = features.loadToString(reviews_sent)
    reviews_pos_str = features.loadToString(reviews_pos_sent)
    reviews_neg_str = features.loadToString(reviews_neg_sent)


    # Summarize all strings
    # Let the algorithm decide the size of the summary
    ratio = 0.5
    reviews_str = features.summarizeString(reviews_str, ratio)
    reviews_pos_str = features.summarizeString(reviews_pos_str, ratio)
    reviews_neg_str = features.summarizeString(reviews_neg_str, ratio)


    # Strings to sentences
    sent_full_review = features.stringToSentences(reviews_str)
    sent_pos_review = features.stringToSentences(reviews_pos_str)
    sent_neg_review = features.stringToSentences(reviews_neg_str)
    # print(sent_full_review[0])

    # Time to remove all the stop words
    # Before tokenization

    sent_full_review_clean = []
    for sentence in tqdm(sent_full_review):
        sent_full_review_clean.append(languageUtils.clean(sentence, remove_stopwords=True))

    sent_pos_review_clean = []
    for sentence in tqdm(sent_pos_review):
        sent_pos_review_clean.append(languageUtils.clean(sentence, remove_stopwords=True))

    sent_neg_review_clean = []
    for sentence in tqdm(sent_neg_review):
        sent_neg_review_clean.append(languageUtils.clean(sentence, remove_stopwords=True))

    print("Cleaned : " + str(len(sent_full_review_clean)) + " all sentences")
    print("Cleaned : " + str(len(sent_pos_review_clean)) + " positive sentences")
    print("Cleaned : " + str(len(sent_neg_review_clean)) + " negative sentences")


    # Getting the most relevant items from the reviews
    items = []
    rules = []
    minSupport = .1
    minConfidence = .6

    items, rules = languageUtils.getItems(sent_full_review_clean, minSupport, minConfidence)
    print('Found ' + str(len(items)) + ' significant items/nouns from the reviews')
    print(items)

    # # Good time to TFIDF
    # # On clean sentences
    # vectorizer_pos = TfidfVectorizer(ngram_range=(2,3))
    # tf_pos = vectorizer_pos.fit_transform(sent_pos_review_clean)
    # feature_names_pos = vectorizer_pos.get_feature_names()
    # phrase_scores_pos = vectorizer_pos.idf_
    # names_scores_df_pos = pd.DataFrame({'feature_names':feature_names_pos})
    # names_scores_df_pos['phrase_scores'] = pd.DataFrame(phrase_scores_pos)
    # print('TFIDF Data Frame size: ' + str(names_scores_df_pos.size) + ' For positive sentences')
    #
    # vectorizer_neg = TfidfVectorizer(ngram_range=(2,3))
    # tf_neg = vectorizer_neg.fit_transform(sent_neg_review_clean)
    # feature_names_neg = vectorizer_neg.get_feature_names()
    # phrase_scores_neg = vectorizer_neg.idf_
    # names_scores_df_neg = pd.DataFrame({'feature_names':feature_names_neg})
    # names_scores_df_neg['phrase_scores'] = pd.DataFrame(phrase_scores_neg)
    # print('TFIDF Data Frame size: ' + str(names_scores_df_neg.size) + ' For negative sentences')

    # Patterns that we want to extract
    # We think these are the ones that contain features
    feature_patterns = r"""
        P1:{<JJ><NN|NNS>}
        P2:{<JJ><NN|NNS><NN|NNS>}
        P3:{<RB|RBR|RBS><JJ>}
        P4:{<RB|RBR|RBS><JJ|RB|RBR|RBS><NN|NNS>}
        P5:{<RB|RBR|RBS><VBN|VBD>}
        P6:{<RB|RBR|RBS><RB|RBR|RBS><JJ>}
        P7:{<VBN|VBD><NN|NNS>}
        P8:{<VBN|VBD><RB|RBR|RBS>}
    """

    extracted_pos = []
    extracted_neg = []
    extracted_neutral = []

    # extracted_neutral, extracted_pos, extracted_neg = features.extractFeaturePhrases(sent_pos_review, sent_neg_review, feature_patterns, items)
    extracted_neutral, extracted_pos, extracted_neg = features.extractFeaturePhrasesStrict(sent_pos_review, sent_neg_review, feature_patterns, items)

    # Convert all phrases to real words
    extracted_pos_real = languageUtils.getRealWordsAll(extracted_pos)
    extracted_neg_real = languageUtils.getRealWordsAll(extracted_neg)


    # # Frequency distribution
    # freqdist_pos = nltk.FreqDist(word for word in extracted_pos_real)
    # most_common_pos = freqdist_pos.most_common()
    # freqdist_neg = nltk.FreqDist(word for word in extracted_neg_real)
    # most_common_neg = freqdist_neg.most_common()

    # Frequency distribution
    freqdist_pos = nltk.FreqDist(word for word in extracted_pos)
    most_common_pos = freqdist_pos.most_common(20)
    print('Most common RAW phrases from the positive reviews: ')
    pprint(most_common_pos)
    freqdist_neg = nltk.FreqDist(word for word in extracted_neg)
    most_common_neg = freqdist_neg.most_common(20)
    print('Most common RAW phrases from the negative reviews: ')
    pprint(most_common_neg)

    # Convert most common phrases to real words
    most_common_pos_real = languageUtils.getRealWords(most_common_pos)
    print('Most common phrases from the positive reviews: ')
    pprint(most_common_pos_real)
    most_common_neg_real = languageUtils.getRealWords(most_common_neg)
    print('Most common phrases from the negative reviews: ')
    pprint(most_common_neg_real)

    # # bi-gram and tri-gram features that are also our extracted phrases
    # extracted_df_pos = names_scores_df_pos[names_scores_df_pos.feature_names.isin(extracted_pos_real)]
    # # print(extracted_df_pos.size)
    # print('Reduced TFIDF Data Frame size: ' + str(extracted_df_pos.size) + ' For positive sentences')
    # extracted_df_pos['freq'] = extracted_df_pos.apply(lambda row: freqdist_pos[row.feature_names], axis=1)
    #
    # extracted_df_neg = names_scores_df_neg[names_scores_df_neg.feature_names.isin(extracted_neg_real)]
    # # print(extracted_df_neg.size)
    # print('Reduced TFIDF Data Frame size: ' + str(extracted_df_neg.size) + ' For negative sentences')
    # extracted_df_neg['freq'] = extracted_df_neg.apply(lambda row: freqdist_neg[row.feature_names], axis=1)

    # Sort the items by support
    items.sort(key=lambda tup: tup[1], reverse=True)
    print('Sorted significant nouns/items list: ')
    print(items)

    # Latest time in a string
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # Outputfile
    print("Files created at: " + timestr)
    output_file_pos = "o_" + "pos_" + timestr + ".json"
    output_file_neg = "o_" + "neg_" + timestr + ".json"

    # featuresAndContext(item_arr, opinion_phrases, sentence_arr, phrase_count, sentence_count )
    # Getting sentences with the positive phrases
    out_json_s_pos = features.featuresAndContext(items, most_common_pos_real, sent_pos_review, 10, 10)
    with open(output_file_pos, 'w') as jf:
        jf.write(out_json_s_pos)
    print("Positive phrases written to: " + output_file_pos)

    # Getting sentences with the negative phrases
    out_json_s_neg = features.featuresAndContext(items, most_common_neg_real, sent_neg_review, 10, 10)
    with open(output_file_neg, 'w') as jfn:
        jfn.write(out_json_s_neg)
    print("Negative phrases written to: " + output_file_neg)

    return out_json_s_pos, out_json_s_neg

if __name__ == "__main__":
   main(sys.argv[1:])
