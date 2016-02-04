# -*- coding: utf-8 -*-
import numpy as np
import lda
import lda.datasets
import csv
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from gensim import corpora, models
import gensim
from stemming.porter2 import stem
from nltk.stem import *
import unicodecsv
import re

import argparse


list_of_stemmer_choices = ["none", "porter", "porter2"]
parser = argparse.ArgumentParser(description='run LDA on an input csv file.')
parser.add_argument('-i','--input',dest="filename", help='input CSV file', required=True)
parser.add_argument('-s','--stemmer', help='pick stemmer', default="porter2", choices=list_of_stemmer_choices)
parser.add_argument('-ni','--num_iter', help='number of iterations', default="1000")

args = parser.parse_args()

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

def process_tokens(tokens,stemmer):
  tokens = [i for i in tokens if not i in en_stop and not contains_digits(i)]
  if stemmer == 'porter':
    tokens = [stem(i) for i in tokens]
  elif stemmer == 'porter2':
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(i) for i in tokens]

  return tokens





f = open(args.filename)
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
for idx,i in enumerate(contents):
  if not idx % 10:
    print "INFO: Tokenizing articles <{}> ".format(idx)
  raw = i.lower()
  tokens = tokenizer.tokenize(raw)
  texts.append(process_tokens(tokens, args.stemmer))
  # print idx
  # add tokens to list

print "[DEBUG] Length of Texts : {}".format(len(texts))
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

X = np.zeros((len(contents), len(dictionary)), dtype=np.int)
for idx,i in enumerate(corpus):
  for j in i:
    X[idx][j[0]] = j[1]

model = lda.LDA(n_topics=20, n_iter=int(args.num_iter), random_state=1)
model.fit(X)


n_top_words = 8
topic_word = model.topic_word_  # model.components_ also works
for i, topic_dist in enumerate(topic_word):
  topic_words = [ dictionary[x] for x in np.array(dictionary)[np.argsort(topic_dist)][:-(n_top_words+1):-1] ]
  print u'Topic {}: {}'.format(i, ' '.join(topic_words))
doc_topic = model.doc_topic_
for i in range(10):
   print u'"{} (top topic: {})"'.format(titles[i], doc_topic[i].argmax())