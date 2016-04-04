# -*- coding: utf-8 -*-
import numpy as np
import lda
import csv
from lib.utils import *
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
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


list_of_stemmer_choices = ["none", "porter", "porter2", "lemma"]
list_of_model_choices = ["lda", "dtm"]
list_of_dictionary_choices = ["none", "technology", "automotive", "english"]
parser = argparse.ArgumentParser(description='run LDA on an input csv file.')
parser.add_argument('-i','--input',dest="filename", help='input CSV file', required=True)
parser.add_argument('-s','--stemmer', help='pick stemmer', default="lemma", choices=list_of_stemmer_choices)
parser.add_argument('-ni','--num_iter', help='number of iterations', default="20")
parser.add_argument('-ntw','--num_top_words', help='number of top_words', default="8")
parser.add_argument('-nt','--num_topics', help='number of topics', default="10")
parser.add_argument('-m', '--model', help='model used', default='lda', choices=list_of_model_choices)
parser.add_argument('-d', '--dictionary', help='dictionary used', default='english', choices=list_of_dictionary_choices)

args = parser.parse_args()

dir = os.getcwd()
model_dir = os.path.join(dir, 'models/')
dataset_dir = os.path.join(dir, 'datasets/')
dictionary_dir = os.path.join(dir, 'dictionaries/')
executable_dir = os.path.join(dir, 'executables/')


load_from_dictionary(args.dictionary)







model_filename = os.path.join(model_dir, get_model_with_arguments_filename(args))
print model_filename
try:
  ldamodel = models.LdaModel.load(model_filename)
except IOError:
  dataset_filepath = os.path.join(dataset_dir, args.filename)
  f = open(dataset_filepath)
  reader = unicodecsv.reader(f, encoding='utf-8')
  # csv_length = sum(1 for row in reader)
  # f.seek(0) #reset reader position
  identifiers = reader.next()
  contents_idx = identifiers.index("contents")
  title_idx = identifiers.index("title")

  contents = [ row[contents_idx] for row in reader if row[contents_idx] ]

  f.seek(0)
  reader.next()
  titles = [ row[title_idx] for row in reader if row[contents_idx] ]
  texts = list()
  tokenizer = RegexpTokenizer(r'\w+')
  en_stop = get_stop_words('en')
  print "Tokenizing ..."
  texts = [ process_tokens(tokenizer.tokenize(word.lower()), args.stemmer) for word in contents ]

  print "[DEBUG] Length of Texts : {}".format(len(texts))
  dictionary = corpora.Dictionary(texts)
  corpus = [dictionary.doc2bow(text) for text in texts]
  # my_timeslices = [500,500,500,500,500,346]
  # my_timeslices = [300,300,300,300,300, 312]
  # my_timeslices = [500,500,500,500,500, 346]
  my_timeslices = [50,50,50,50,20]

  if(args.model == "lda"):
   ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=int(args.num_topics), id2word = dictionary, passes=int(args.num_iter))
  elif(args.model == "dtm"):
    ldamodel = gensim.models.wrappers.DtmModel(get_exec_dir('dtm-darwin64'), corpus, my_timeslices, num_topics=int(args.num_topics), id2word=dictionary,initialize_lda=True)
  else:
    raise ValueError('Unknown Model Type')

  ldamodel.save(model_filename)

show_topics(args.model, ldamodel, args.num_topics, args.num_top_words)