from tqdm import tqdm
import numpy as np
import os
import pandas as pd
import re
from . import languageUtils


batch_size = 64
epochs = 110
latent_dim = 256
num_samples = 10000

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
    sum_sent = []
    sum_neg_sent = []
    sum_pos_sent = []

    for r in tqdm(file_d):
        if (filter_l and (r['asin'] == filter_l)) or not filter_l:
            reviews_sent.append(languageUtils.clean(r['reviewText']))
            sum_sent.append(languageUtils.clean('_START_ ' + r['summary'] + ' _END_'))
            if ((r['overall'] == 1.0) or (r['overall'] == 2.0)):
                reviews_neg_sent.append(languageUtils.clean(r['reviewText']))
                sum_neg_sent.append(languageUtils.clean('_START_ ' + r['summary'] + ' _END_'))
            else:
                reviews_pos_sent.append(languageUtils.clean(r['reviewText']))
                sum_pos_sent.append(languageUtils.clean('_START_ ' + r['summary'] + ' _END_'))

            n = n+1
            if count > 0 and n == count:
                break

    print("Processed and Classified " + str(n) + " Reviews")
    print(str(len(reviews_pos_sent)) + " Positive reviews")
    print(str(len(reviews_neg_sent)) + " Negative reviews")
    return reviews_sent, reviews_pos_sent, reviews_neg_sent, sum_sent, sum_pos_sent, sum_neg_sent


# def loadReviewsIntoLists(reviews):
#
#     input_texts = []
#     target_texts = []
#
#     for review in reviews:
#         input_text = review['reviewText']
#         target_text = review['summary']
#         input_texts.append(input_text)
#         target_texts.append(target_text)
#         for char in input_text:
#             if char not in input_characters:
#                 input_characters.add(char)
#         for char in target_text:
#             if char not in target_characters:
#                 target_characters.add(char)
#
#     input_characters = sorted(list(input_characters))
#     target_characters = sorted(list(target_characters))
#
#     num_encoder_tokens = len(input_characters)
#     num_decoder_tokens = len(target_characters)
#
#     max_encoder_seq_length = max([len(txt) for txt in input_texts])
#     max_decoder_seq_length = max([len(txt) for txt in target_texts])
#
#     print('Number of samples:', len(input_texts))
#     print('Number of unique input tokens:', num_encoder_tokens)
#     print('Number of unique output tokens:', num_decoder_tokens)
#     print('Max sequence length for inputs:', max_encoder_seq_length)
#     print('Max sequence length for outputs:', max_decoder_seq_length)
#
#     return input_texts, target_texts, input_characters, target_characters
#
#
# def loadReviewsIntoLists(reviews):
#
#     input_texts = []
#     target_texts = []
#     input_characters = set()
#     target_characters = set()
#
#     for review in reviews:
#         input_text = review['reviewText']
#         target_text = review['summary']
#         input_texts.append(input_text)
#         target_texts.append(target_text)
#         for char in input_text:
#             if char not in input_characters:
#                 input_characters.add(char)
#         for char in target_text:
#             if char not in target_characters:
#                 target_characters.add(char)
#
#     input_characters = sorted(list(input_characters))
#     target_characters = sorted(list(target_characters))
#
#     num_encoder_tokens = len(input_characters)
#     num_decoder_tokens = len(target_characters)
#
#     max_encoder_seq_length = max([len(txt) for txt in input_texts])
#     max_decoder_seq_length = max([len(txt) for txt in target_texts])
#
#     print('Number of samples:', len(input_texts))
#     print('Number of unique input tokens:', num_encoder_tokens)
#     print('Number of unique output tokens:', num_decoder_tokens)
#     print('Max sequence length for inputs:', max_encoder_seq_length)
#     print('Max sequence length for outputs:', max_decoder_seq_length)
#
#     return input_texts, target_texts, input_characters, target_characters
#
#
# def define_models(n_input, n_output, n_units):
#
#     # define training encoder
#     encoder_inputs = Input(shape=(None, n_input))
#     encoder = LSTM(n_units, return_state=True)
#     encoder_outputs, state_h, state_c = encoder(encoder_inputs)
#     encoder_states = [state_h, state_c]
#
#     # define training decoder
#     decoder_inputs = Input(shape=(None, n_output))
#     decoder_lstm = LSTM(n_units, return_sequences=True, return_state=True)
#     decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
#     decoder_dense = Dense(n_output, activation='softmax')
#     decoder_outputs = decoder_dense(decoder_outputs)
#
#     model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
#
#     # define inference encoder
#     encoder_model = Model(encoder_inputs, encoder_states)
#
#     # define inference decoder
#     decoder_state_input_h = Input(shape=(n_units,))
#     decoder_state_input_c = Input(shape=(n_units,))
#     decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
#     decoder_outputs, state_h, state_c = decoder_lstm(decoder_inputs,  initial_state=decoder_states_inputs)
#     decoder_states = [state_h, state_c]
#     decoder_outputs = decoder_dense(decoder_outputs)
#
#     decoder_model = Model([decoder_inputs] + decoder_states_inputs, [decoder_outputs] + decoder_states)
#
#     # return all models
#
#     return model, encoder_model, decoder_model
#
# def train():
#     optimizer = 'rmsprop'
#     loss = 'categorical_crossentropy'
#     batch_size = batch_size
#     epochs = epochs
#     validation_split = .2
#
#     model.compile(optimizer, loss)
#     model.fit([encoder_input_data, decoder_input_data], decoder_target_data, batch_size, epochs, validation_split)
#     model.save(model_name)
