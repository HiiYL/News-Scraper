import os
import numpy as np
import lda
import csv
from lib.utils import *
from nltk.tokenize import RegexpTokenizer
from gensim import corpora, models

from stemming.porter2 import stem
from nltk.stem import *
import unicodecsv
import re
import os
# import pyLDAvis.gensim
import gensim
import argparse

# Using PyEnchant spell checker purpose
import enchant
from stop_words import get_stop_words


dir = os.getcwd()
model_dir = os.path.join(dir, 'models/')
dataset_dir = os.path.join(dir, 'datasets/')
dictionary_dir = os.path.join(dir, 'dictionaries/')
executable_dir = os.path.join(dir, 'executables/')


_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))


def get_dict_dir(s):
  return os.path.join(dictionary_dir, s)

def get_exec_dir(s):
  return os.path.join(executable_dir, s)


# Or using the /usr/share/dict/british-english word list
def load_from_dictionary(dictionary):
  if dictionary == "none":
    def is_english_word(word):
      return True
  elif dictionary == "english":
    d = enchant.Dict("en_US")
    def is_english_word(word):
      return d.check(word)
  else:
    with open(get_dict_dir(dictionary + "-english")) as word_file:
      english_words = set(word.strip().lower() for word in word_file)
      # print(english_words)
      def is_english_word(word):
        return word.lower() in english_words
  return is_english_word

def process_tokens(tokens,stemmer,is_english_word):
  en_stop = get_stop_words('en')
  tokens = [i for i in tokens if not i in en_stop and not contains_digits(i) and is_english_word(i)]
  if stemmer == 'porter':
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(i) for i in tokens]
  elif stemmer == 'porter2':
    tokens = [stem(i) for i in tokens]
  elif stemmer == 'lemma':
    lemmatiser = WordNetLemmatizer()
    tokens = [lemmatiser.lemmatize(i) for i in tokens]
  return tokens

def generate_model(model_type, corpus, dictionary, num_topics, num_iters):
  # my_timeslices = [500,500,500,500,500,346]
  # my_timeslices = [300,300,300,300,300, 312]
  # my_timeslices = [500,500,500,500,500, 346]
  my_timeslices = [50,50,50,50,20]
  if(model_type == "lda"):
   ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=int(num_topics), id2word = dictionary, passes=int(num_iter))
  elif(model_type == "dtm"):
    ldamodel = gensim.models.wrappers.DtmModel(get_exec_dir('dtm-darwin64'), corpus, my_timeslices, num_topics=int(num_topics), id2word=dictionary,initialize_lda=True)
  else:
    raise ValueError('Unknown Model Type')
  return ldamodel


def show_topics(model_type, model, num_topics, num_top_words):
  if model_type == "lda" :
    for topic in model.show_topics(num_topics=num_topics, num_words=int(num_top_words), log=False, formatted=False):
      print "Topic #" + str(topic[0]) + " :",
      for word in topic[1]:
        print word[0],
      print
  elif model_type == "dtm" :
    for idx, topic in enumerate(model.show_topics(topics=num_topics, topn=int(num_top_words),times=1, formatted=False)):
      print "Topic #" + str(idx) + " :",
      for word in topic:
        print word[1],
      print
  else:
    print "Uh-oh unknown model detected, fix me at utils.py"

def get_model_with_arguments_filename(args):
  return (args.filename.split('.')[0] + "_" + args.stemmer + "_" + args.num_iter +
   "_" + args.num_top_words + "_" + args.num_topics  + "_" + args.model + "_" + args.dictionary)