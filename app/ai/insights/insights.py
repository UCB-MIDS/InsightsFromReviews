from . import languageUtils
from . import features
from tqdm import tqdm
import nltk
import sys
import getopt
import json
import time

# This implements the NLP pipeline

def main(argv):

    # Usage
    try:
      opts, args = getopt.getopt(argv,"hi:j:a:c:",["dbfile=", "jsonString", "asin", "count"])
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
    print(len(reviews_str))

    # Strings to sentences
    sent_full_review = features.stringToSentences(reviews_str)
    sent_pos_review = features.stringToSentences(reviews_pos_str)
    sent_neg_review = features.stringToSentences(reviews_neg_str)
    # print(sent_full_review[0])

    # Getting the most relevant items from the reviews
    items = []
    rules = []
    minSupport = .3
    minConfidence = .4

    items, rules = languageUtils.getItems(sent_full_review, minSupport, minConfidence)
    print(len(items))
    print(items)

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

    # Frequency distribution
    freqdist_pos = nltk.FreqDist(word for word in extracted_pos)
    most_common_pos = freqdist_pos.most_common()
    freqdist_neg = nltk.FreqDist(word for word in extracted_neg)
    most_common_neg = freqdist_neg.most_common()

    # Convert phrases to real words
    most_common_pos_real = languageUtils.getRealWords(most_common_pos)
    print(most_common_pos_real)
    most_common_neg_real = languageUtils.getRealWords(most_common_neg)
    print(most_common_neg_real)

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
    print("Pos phrases written to: " + output_file_pos)

    # Getting sentences with the negative phrases
    out_json_s_neg = features.featuresAndContext(items, most_common_neg_real, sent_neg_review, 10, 10)
    with open(output_file_neg, 'w') as jfn:
        jfn.write(out_json_s_neg)
    print("Neg phrases written to: " + output_file_neg)

    return out_json_s_pos, out_json_s_neg

if __name__ == "__main__":
   main(sys.argv[1:])
