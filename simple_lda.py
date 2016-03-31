# -*- coding: utf-8 -*-
import numpy as np
import lda
import csv
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


_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))


def get_dict_dir(s):
  return os.path.join(dictionary_dir, s)

def get_exec_dir(s):
  return os.path.join(executable_dir, s)

d = enchant.Dict("en_US")
# Or using the /usr/share/dict/british-english word list
if args.dictionary != "none":
  with open(get_dict_dir(args.dictionary + "-english")) as word_file:
    english_words = set(word.strip().lower() for word in word_file)
    # print(english_words)
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


def get_model_with_arguments_filename():
  return (args.filename.split('.')[0] + "_" + args.stemmer + "_" + args.num_iter +
   "_" + args.num_top_words + "_" + args.num_topics  + "_" + args.model)



if args.filename == "sample":
  X = lda.datasets.load_reuters()
  dictionary = lda.datasets.load_reuters_vocab()
  titles = lda.datasets.load_reuters_titles()
else:
  # X = np.zeros((len(contents), len(dictionary)), dtype=np.int)
  # for idx,i in enumerate(corpus):
  #   for j in i:
  #     X[idx][j[0]] = j[1]

  model_filename = os.path.join(model_dir, get_model_with_arguments_filename())
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
    # my_timeslices = [500,500,500,500,500,346]
    my_timeslices = [500,500,500,500,500, 346]

    if(args.model == "lda"):
     ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=int(args.num_topics), id2word = dictionary, passes=int(args.num_iter))
    elif(args.model == "dtm"):
      ldamodel = gensim.models.wrappers.DtmModel(get_exec_dir('dtm-darwin64'), corpus, my_timeslices, num_topics=int(args.num_topics), id2word=dictionary,initialize_lda=True)
    else:
      raise ValueError('Unknown Model Type')

    ldamodel.save(model_filename)

if(args.model == "lda"):
  for topic in ldamodel.show_topics(num_topics=args.num_topics, num_words=int(args.num_top_words), log=False, formatted=False):
    print "Topic #" + str(topic[0]) + " :",
    for word in topic[1]:
      print word[0],
    print
else:
  for idx, topic in enumerate(ldamodel.show_topics(topics=args.num_topics, topn=int(args.num_top_words),times=1, formatted=False)):
    print "Topic #" + str(idx) + " :",
    for word in topic:
      print word[1],
    print

# print ldamodel.show_topics(num_topics=10, num_words=10, log=False, formatted=True)
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