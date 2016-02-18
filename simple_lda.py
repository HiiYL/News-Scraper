# -*- coding: utf-8 -*-
import numpy as np
import lda
import lda.datasets
import csv
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from gensim import corpora, models

from stemming.porter2 import stem
from nltk.stem import *
import unicodecsv
import re
import pyLDAvis.gensim
import gensim

import argparse


list_of_stemmer_choices = ["none", "porter", "porter2", "lemma"]
parser = argparse.ArgumentParser(description='run LDA on an input csv file.')
parser.add_argument('-i','--input',dest="filename", help='input CSV file', required=True)
parser.add_argument('-s','--stemmer', help='pick stemmer', default="porter2", choices=list_of_stemmer_choices)
parser.add_argument('-ni','--num_iter', help='number of iterations', default="1000")
parser.add_argument('-ntw','--num_top_words', help='number of top_words', default="8")
parser.add_argument('-nt','--num_topics', help='number of topics', default="10")
args = parser.parse_args()

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

# Playing around with just dictionary words
# Using PyEnchant spell checker purpose
import enchant
d = enchant.Dict("en_US")
# Or using the /usr/share/dict/british-english word list
with open("automotive-english") as word_file:
  english_words = set(word.strip().lower() for word in word_file)
  print(english_words)
  def is_english_word(word):
    return word.lower() in english_words

def process_tokens(tokens,stemmer):
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


if args.filename == "sample":
  X = lda.datasets.load_reuters()
  dictionary = lda.datasets.load_reuters_vocab()
  titles = lda.datasets.load_reuters_titles()
else:
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

  # X = np.zeros((len(contents), len(dictionary)), dtype=np.int)
  # for idx,i in enumerate(corpus):
  #   for j in i:
  #     X[idx][j[0]] = j[1]
  model_filename = args.filename.split('.')[0] + '.model'
  try:
    ldamodel = models.LdaModel.load(model_filename)
  except IOError:
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=10, id2word = dictionary, passes=5)
    ldamodel.save(model_filename)


# model = lda.LDA(n_topics=int(args.num_topics), n_iter=int(args.num_iter), random_state=1)
# model.fit(X)
print ldamodel.show_topics(num_topics=10, num_words=10, log=False, formatted=True)
# n_top_words = int(args.num_top_words)
# topic_word = ldamodel.get_topic_terms  # odel.components_ also works
# for i, topic_dist in enumerate(topic_word):
#   if args.filename == "sample":
#     topic_words = np.array(dictionary)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
#   else:
#     topic_words = [ dictionary[x] for x in np.array(dictionary)[np.argsort(topic_dist)][:-(n_top_words+1):-1] ]
#   print u'Topic {}: {}'.format(i, ' '.join(topic_words))
# doc_topic = model.doc_topic_
# for i in range(10):
#    print u'"{} (top topic: {})"'.format(titles[i], doc_topic[i].argmax())