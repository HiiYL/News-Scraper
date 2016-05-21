import os
import numpy as np
import lda
import csv
from nltk.tokenize import RegexpTokenizer
from gensim import corpora, models, similarities, matutils

from stemming.porter2 import stem as porter_stem
from nltk.stem import *
import unicodecsv
import re
import os
# import pyLDAvis.gensim
import gensim
import argparse
import numpy as np

# Using PyEnchant spell checker purpose
import enchant

from dateutil import parser
from datetime import timedelta

import pandas as pd
# import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
#     level=logging.INFO)

import scipy.stats as stats

from collections import defaultdict
# import matplotlib.pyplot as plt
# import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
#     level=logging.INFO)
# import numpy as np

# import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

dir = os.getcwd()
model_dir = os.path.join(dir, 'models/')
dataset_dir = os.path.join(dir, 'datasets/')
dictionary_dir = os.path.join(dir, 'dictionaries/')
executable_dir = os.path.join(dir, 'executables/')
all_words_dir = os.path.join(dir, 'allwords/')
tagged_dataset_dir = os.path.join(dir, 'tagged_datasets/')

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

_contain_letters = re.compile('[a-zA-Z]')
def contains_letters(d):
  return bool(_contain_letters.search(d))


def get_dict_dir(s):
  return os.path.join(dictionary_dir, s)

def get_exec_dir(s):
  return os.path.join(executable_dir, s)

with open(get_dict_dir("stop_words.txt")) as word_file:
  stop_words = set(word.strip().lower() for word in word_file)

def add_to_stopwords(input):
  if input != None:
    # print "ADDING TO STOPWORDS"
    # print "Length of stopwords before", len(stop_words)
    with open(get_dict_dir(input)) as word_file:
      [ stop_words.add(word.strip().lower()) for word in word_file ]
    # print "Length of stopwords after", len(stop_words)




def preprocess(contents, stemmer, is_english_word):
  all_words_tokenized = [tokenize(text, is_english_word) for text in contents]
  all_words_stemmed = [tokenize_and_stem(text,stemmer, is_english_word) for text in contents]

  return all_words_tokenized, all_words_stemmed

def tokenize_and_stem(text, stemmer="lemma", is_english_word=None):
  if is_english_word == None:
    is_english_word = load_from_dictionary("english")

  tokenizer = RegexpTokenizer(r'\w+')
  return stem(tokenize(text, is_english_word), stemmer)

def tokenize(text, is_english_word):
  tokenizer = RegexpTokenizer(r'\w+')
  tokens = tokenizer.tokenize(text.lower())
  filtered_tokens = [i for i in tokens if not i in stop_words and not contains_digits(i) and is_english_word(i)]
  return filtered_tokens

def stem(tokens, stemmer):
  if stemmer == 'porter':
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(i) for i in tokens]
  elif stemmer == 'porter2':
    tokens = [stem(i) for i in tokens]
  elif stemmer == 'lemma':
    lemmatiser = WordNetLemmatizer()
    tokens = [lemmatiser.lemmatize(i) for i in tokens]

  return tokens



def load_model(model_path, model_type):
  if model_type == "lda":
    model = models.LdaModel.load(model_path)
  elif model_type == "dtm":
    model = models.wrappers.DtmModel.load(model_path)
  return model

# Or using the /usr/share/dict/british-english word list
def load_from_dictionary(dictionary, added_dictionary=None):
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
    if added_dictionary != None:
      with open(get_dict_dir(added_dictionary)) as word_file:
        [ english_words.add(word.strip().lower()) for word in word_file ]
    def is_english_word(word):
      return word.lower() in english_words
  return is_english_word



def generate_model(model_type, corpus, dictionary, num_topics, num_iter,dates="", timedelta=""):
  # my_timeslices = [237,237,237,237,237,237,237,237,237,237,237,239] #paultan

  # my_timeslices = [144,144,144,144,144,144,144,144,144,144,144,149] #soya_year
  # my_timeslices = [ 450,450,450,450,450,450,450,450,450,450,450,433]
  # my_timeslices = [50,50,50,50,50,29]
  if(model_type == "lda"):
   ldamodel = gensim.models.LdaMulticore(corpus, workers = 1, num_topics=int(num_topics), id2word = dictionary, passes=int(num_iter))
  elif(model_type == "dtm"):
    my_timeslices = generate_timeslices(dates,timedelta) # soya_month
    print my_timeslices
    ldamodel = gensim.models.wrappers.DtmModel(get_exec_dir('dtm-darwin64'), corpus, my_timeslices, num_topics=int(num_topics), id2word=dictionary,initialize_lda=True)
  else:
    raise ValueError('Unknown Model Type')
  return ldamodel


def show_topics(model_type, model, num_topics, num_top_words,titles, corpus):
  if model_type == "lda" :
    topics = model.show_topics(num_topics=num_topics, num_words=int(num_top_words), log=False, formatted=False)
    for topic in topics:
      print "Topic #" + str(topic[0]) + " :",
      for word in topic[1]:
        print word[0],
      print
    print
    for i in range(10):
      print str(i) + " : ",
      print titles[i],
      print "(top topic: {})".format(str(max(model.get_document_topics(corpus)[i],key=lambda item:item[1])[0]))
      # print model.get_document_topics(corpus)[i]
      # print  titles[i] + " : " + model.get_document_topics(corpus)[i]
  elif model_type == "dtm" :
    for idx, topic in enumerate(model.show_topics(topics=num_topics, topn=int(num_top_words),times=1, formatted=False)):
      print "Topic #" + str(idx) + " :",
      for word in topic:
        print word[1],
      print
  else:
    print "Uh-oh unknown model detected, fix me at utils.py"

def save(model,corpus,input_dataset_path, output_dataset_path):
  print "Saving to " + output_dataset_path
  # list_of_topic_id = []
  # for topic in model.get_document_topics(corpus):
  #   list_of_topic_id.append([str(max(topic,key=lambda item:item[1])[0])])

  # df= pd.DataFrame({'topic': list_of_topic_id})

  # # dataframe = dataframe.join(df)

  # dataframe.to_csv(output_dataset_path, encoding='utf-8')

  with open(input_dataset_path, 'rb') as input, open(output_dataset_path, 'wb') as output:
    reader = unicodecsv.reader(input, encoding='utf-8')
    writer = unicodecsv.writer(output, encoding='utf-8')

    all = []
    row = next(reader)
    row.append('topic')
    all.append(row)
    for i, row in enumerate(reader):
        all.append(row + [str(max(model.get_document_topics(corpus)[i],key=lambda item:item[1])[0])])
    writer.writerows(all)

def get_model_with_arguments_filename(args):
  return (args.filename.split('.')[0] + "_" + args.stemmer + "_" + str(args.num_iter) +
   "_" + "8" + "_" + str(args.num_topics)  + "_" + args.model + "_" + args.dictionary
   + get_input_field(args)) ##hardcoded number_top_words to retain compatiblity with previously trained models

def get_input_field(args):
  if (args.input_field == "contents"):
    return ""
  else:
    return ("_" + args.input_field)

#From http://blog.cigrainger.com/tag/python-lda-gensim.html
# Define KL function
def sym_kl(p,q):
    return np.sum([stats.entropy(p,q),stats.entropy(q,p)])

def arun(corpus,dictionary,max_topics,min_topics=1,step=1):
  l = np.array([sum(cnt for _, cnt in doc) for doc in corpus])
  kl = []
  for i in range(min_topics,max_topics,step):
      print "Current Topic " + str(i)
      lda = models.ldamodel.LdaModel(corpus=corpus,
          id2word=dictionary,num_topics=i)
      m1 = lda.expElogbeta
      U,cm1,V = np.linalg.svd(m1)
      #Document-topic matrix
      lda_topics = lda[corpus]
      m2 = matutils.corpus2dense(lda_topics, lda.num_topics).transpose()
      cm2 = l.dot(m2)
      cm2 = cm2 + 0.0001
      cm2norm = np.linalg.norm(l)
      cm2 = cm2/cm2norm
      kl.append(sym_kl(cm1,cm2))
  return kl


def generate_timeslices(dates, time_delta):
  initial_date = dates[0]
  curr_bucket = 1
  current_bucket_count = 0
  buckets = []
  for date in dates:
    if date > (initial_date - curr_bucket * time_delta):
      current_bucket_count = current_bucket_count + 1
    else:
      buckets.append(current_bucket_count)
      current_bucket_count = 1
      curr_bucket = curr_bucket + 1
  buckets.append(current_bucket_count)
  return buckets

def add_to_dict(s):
  with open(s) as word_file:
    for word in word_file:
      english_words.add(word.strip().lower())

def write_to_dict(s):
  with open(s, 'wb') as output:
    for word in english_words:
        output.write(word+'\n')

def generate_allwords(texts, args):
  text_separated = [ item for innerlist in texts for item in innerlist ]
  with open(os.path.join(all_words_dir, args.filename + "_" + args.dictionary 
    + "_" + args.input_field + ".txt"), 'wb') as outfile:
    outfile.write("\n".join(text_separated).encode("UTF-8"))


def remove_stems_from_file():
  dir = os.getcwd()
  dictionary_dir = os.path.join(dir, 'dictionaries/')
  md = defaultdict(list)
  with open(os.path.join(dictionary_dir, 'temp-extend-technology')) as f:
    for word in f:
      word = word.strip()
      md[porter_stem(word)].append(word)
  with open(os.path.join(dictionary_dir, 'temp-extend-technology-unique'), 'wb') as output:
    for k,v in md.iteritems():
      output.write(v[0] + "\n")
      if len(v) > 1:
        print v


def remove_stems(text, output_file):
  dictionary_dir = os.path.join(dir, 'dictionaries/')
  md = defaultdict(list)
  for word in text:
    word = word.strip()
    md[porter_stem(word)].append(word)
  with open(os.path.join(dictionary_dir, output_file), 'wb') as output:
    for k,v in md.iteritems():
      output.write(v[0] + "\n")
      if len(v) > 1:
        print v
