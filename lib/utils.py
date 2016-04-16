import os
import numpy as np
import lda
import csv
from lib.utils import *
from nltk.tokenize import RegexpTokenizer
from gensim import corpora, models, similarities, matutils

from stemming.porter2 import stem
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
from stop_words import get_stop_words

# import scipy.stats as stats
# import matplotlib.pyplot as plt
# import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
#     level=logging.INFO)
# import numpy as np


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

def preprocess(contents, stemmer, is_english_word):
  # print "Preprocessing ..."
  tokenizer = RegexpTokenizer(r'\w+')
  texts = [ process_tokens(tokenizer.tokenize(word.lower()), stemmer,is_english_word) for word in contents ]
  return texts

with open(get_dict_dir("stop_words.txt")) as word_file:
  stop_words = set(word.strip().lower() for word in word_file)

def load_model(model_path, model_type):
  if model_type == "lda":
    model = models.LdaModel.load(model_path)
  elif model_type == "dtm":
    model = models.wrappers.DtmModel.load(model_path)
  return model

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
  en_stop = set(get_stop_words('en'))
  tokens = [i for i in tokens if not i in stop_words and not contains_digits(i) and is_english_word(i)]
  if stemmer == 'porter':
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(i) for i in tokens]
  elif stemmer == 'porter2':
    tokens = [stem(i) for i in tokens]
  elif stemmer == 'lemma':
    lemmatiser = WordNetLemmatizer()
    tokens = [lemmatiser.lemmatize(i) for i in tokens]
  return tokens

def generate_model(model_type, corpus, dictionary, num_topics, num_iter):
  # my_timeslices = [237,237,237,237,237,237,237,237,237,237,237,239] #paultan
  my_timeslices = [37,37,37,35] # soya_month
  # my_timeslices = [144,144,144,144,144,144,144,144,144,144,144,149] #soya_year
  # my_timeslices = [ 450,450,450,450,450,450,450,450,450,450,450,433]
  # my_timeslices = [50,50,50,50,50,29]
  if(model_type == "lda"):
   ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=int(num_topics), id2word = dictionary, passes=int(num_iter))
  elif(model_type == "dtm"):
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

def save(model,input_dataset_path, output_dataset_path):
  with open(dataset_filepath, 'rb') as input, open(output_dataset_path, 'wb') as output:
    reader = unicodecsv.reader(input, encoding='utf-8')
    writer = unicodecsv.writer(output, encoding='utf-8')

    all = []
    row = next(reader)
    row.append('topic')
    all.append(row)
    for i, row in enumerate(reader):
        all.append(row + [str(max(model.get_document_topics(my_corpus)[i],key=lambda item:item[1])[0])])
    writer.writerows(all)
def get_model_with_arguments_filename(args):
  return (args.filename.split('.')[0] + "_" + args.stemmer + "_" + str(args.num_iter) +
   "_" + str(args.num_top_words) + "_" + str(args.num_topics)  + "_" + args.model + "_" + args.dictionary + "_"
   + get_input_field(args))

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





