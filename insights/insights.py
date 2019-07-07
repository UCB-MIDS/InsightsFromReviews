import languageUtils
import features
from tqdm import tqdm
import nltk
import sys
import getopt

def main(argv):

    # Usage
    try:
      opts, args = getopt.getopt(argv,"hi:",["dbfile="])
    except getopt.GetoptError:
      print ('insights.py -i <dbfile>')
      sys.exit(2)

    # File with the reviews DB
    file = '/Users/gkhanna/Downloads/reviews_Home_and_Kitchen_5.json'
    for opt, arg in opts:
        if opt == '-h':
             print ('insights.py -i <dbfile> -a <asins>')
             sys.exit()
        elif opt in ("-i", "--dbfile"):
             file = arg

    # Load reviews in a Dictionary
    print('loading reviews from: ' + file)
    file_d = features.loadFromDb(file, count = 0)
    print(len(file_d))
    print(file_d[0])

    # ASIN corresponding to the Iron Skillet
    asins = ['B00006JSUA']

    # Extract all reviews into a string
    reviews_str = ""
    reviews_pos_str = ""
    reviews_neg_str = ""
    reviews_str, reviews_pos_str, reviews_neg_str = features.loadToStringAndClassify(file_d, filter_l = asins )
    print(len(reviews_str))

    # Summarize all strings
    reviews_str = features.summarizeString(reviews_str)
    reviews_pos_str = features.summarizeString(reviews_pos_str)
    reviews_neg_str = features.summarizeString(reviews_neg_str)
    print(len(reviews_str))

    # Strings to sentences
    sent_full_review = features.stringToSentences(reviews_str)
    sent_neg_review = features.stringToSentences(reviews_neg_str)
    sent_pos_review = features.stringToSentences(reviews_pos_str)
    print(sent_full_review[0])

    # Getting the most relevant items from the reviews
    items = []
    rules = []
    minSupport = .1
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

    extracted_neutral = []
    extracted_neg = []
    extracted_pos = []

    extracted_neutral, extracted_neg, extracted_pos = features.extractFeaturePhrases(sent_pos_review, sent_neg_review, feature_patterns, items)

    # Frequency distribution
    freqdist_pos = nltk.FreqDist(word for word in extracted_pos)
    most_common_pos = freqdist_pos.most_common()
    freqdist_neg = nltk.FreqDist(word for word in extracted_neg)
    most_common_neg = freqdist_neg.most_common()
    print(len(most_common_pos))
    print(len(most_common_neg))
    print(most_common_pos[:10])

    # Convert phrases to real words
    most_common_pos_real = languageUtils.getRealWords(most_common_pos)
    most_common_neg_real = languageUtils.getRealWords(most_common_neg)
    print(most_common_pos_real[:10])

    # Getting sentences with the positive phrases
    out_file_pos = features.featuresAndContext(items, most_common_pos_real, sent_pos_review)
    print("Pos phrases written to: " + out_file_pos)

    # Getting sentences with the negative phrases
    out_file_neg = features.featuresAndContext(items, most_common_neg_real, sent_neg_review)
    print("Neg phrases written to: " + out_file_neg)

if __name__ == "__main__":
   main(sys.argv[1:])
