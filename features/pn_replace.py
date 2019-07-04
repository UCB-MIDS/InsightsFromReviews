'''Pronoun replacement
Python environment must have a spacy model loaded.
Run in shell one time prior to script use:
$ python -m spacy download en_core_web_sm
or
$ python -m spacy download en_core_web_md

'''

import spacy  # version 2.1.3
import neuralcoref  # version 4.0
from textblob import TextBlob
import nltk

# create spacy model
nlp = spacy.load('en_core_web_sm')
# add neuralcoref to spacy model
neuralcoref.add_to_pipe(nlp, greedyness=0.50, max_dist=75)


def remove_pronouns(doc):
    """
    Input: entire review document (str), multiple sentence_scores
    Output: string, modified review with pronouns replaced.
    """

    pn = nlp(doc)  # pn = pronoun doc
    print("has coreferences?  {}".format(pn._.has_coref))
    print("Coreferences:")
    print(pn._.coref_clusters)

    return pn._.coref_resolved


def subjective_sent(doc):
    """
    Input: entire review document (str)
    Output: shortened review document with only subjective sentences
    """
    sent_list = nltk.sent_tokenize(doc)
    output = ""  # output string
    for sent in sent_list:
        result = TextBlob(sent)
        if result.sentiment[1] > 0.20:  # keep sentences with sentiment > 0.25
            output += sent+"  "
    return output


def test_sentence():

    test_sent = "I needed a vacuum but was at a loss because there are so many to choose from.  \
    But one day in the doctor's office, I saw a clip of an asthma prevention program\
    in California and they were recommending Eureka because unlike other vacuums,\
    it doesn't blow the dust back out. Although this is not the exact same model, \
    I like the portability of a cordless and it's a strong vacuum.  \
    I have two dogs and I can get the whole apartment clean and it doesn't even\
    lose its charge so I haven't used the spare battery yet.\
     It's easy to maneuver and there are two settings, one for carpet and one for bare floors.  It's also relatively quiet."

    new_review = subjective_sent(test_sent)

    print("\noriginal review:")
    print("-"*25)
    print(test_sent)

    print("\nsubjective review:")
    print("-"*25)
    print(new_review)

    final_review = remove_pronouns(new_review)
    print("\nFinal review:")
    print("-"*25)
    print(final_review)


test_sentence()
