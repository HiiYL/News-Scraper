# -*- coding: utf-8 -*-
import unicodecsv
import argparse
import os

from lib.utils import *




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

model_filename = os.path.join(model_dir, get_model_with_arguments_filename(args))


is_english_word = load_from_dictionary(args.dictionary)


print model_filename
try:
  ldamodel = models.LdaModel.load(model_filename)
except IOError:
  dataset_filepath = os.path.join(dataset_dir, args.filename)
  f = open(dataset_filepath)
  reader = unicodecsv.reader(f, encoding='utf-8')

  identifiers = reader.next()
  contents_idx = identifiers.index("contents")
  title_idx = identifiers.index("title")

  contents, titles = zip(*[(row[contents_idx], row[title_idx]) for row in reader])

  tokenizer = RegexpTokenizer(r'\w+')
  print "Tokenizing ..."

  texts = [ process_tokens(tokenizer.tokenize(word.lower()), args.stemmer,is_english_word) for word in contents ]
  print "[DEBUG] Length of Texts : {}".format(len(texts))

  dictionary = corpora.Dictionary(texts)
  corpus = [dictionary.doc2bow(text) for text in texts]

  ldamodel = generate_model(args.model, corpus, dictionary, args.num_topics, args.num_iter)
  ldamodel.save(model_filename)

show_topics(args.model, ldamodel, args.num_topics, args.num_top_words)