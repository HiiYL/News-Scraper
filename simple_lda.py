# -*- coding: utf-8 -*-
import unicodecsv
import argparse
import os



from nltk import RegexpTokenizer
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
parser.add_argument('-m', '--model', help='model used', default="dtm", choices=list_of_model_choices)
parser.add_argument('-d', '--dictionary', help='dictionary used', default='english', choices=list_of_dictionary_choices)
parser.add_argument('-o', '--override', action='store_true')
args = parser.parse_args()

dir = os.getcwd()
model_dir = os.path.join(dir, 'models/')
dataset_dir = os.path.join(dir, 'datasets/')
dictionary_dir = os.path.join(dir, 'dictionaries/')
executable_dir = os.path.join(dir, 'executables/')

model_filename = os.path.join(model_dir, get_model_with_arguments_filename(args))


is_english_word = load_from_dictionary(args.dictionary)

print "[INFO] Stemmer               :", args.stemmer
print "[INFO] Number of iterations  :", args.num_iter
print "[INFO] Number of topics      :", args.num_topics
print "[INFO] Number of top words   :", args.num_top_words
print "[INFO] Model used            :", args.model
print "[INFO] Dictionary used       :", args.dictionary
print model_filename
try:
  model = load_model(model_filename, args.model)
  if args.override:
    raise IOError("Override flag set")
except IOError:
  dataset_filepath = os.path.join(dataset_dir, args.filename)
  f = open(dataset_filepath)
  reader = unicodecsv.reader(f, encoding='utf-8')

  identifiers = reader.next()
  contents_idx = identifiers.index("contents")
  title_idx = identifiers.index("title")

  contents, titles = zip(*[(row[contents_idx], row[title_idx]) for row in reader])

  texts = preprocess(contents, args.stemmer, is_english_word)

  dictionary = corpora.Dictionary(texts)

  #remove extremes (similar to the min/max df step used when creating the tf-idf matrix)
  dictionary.filter_extremes(no_below=1, no_above=0.8)
  
  my_corpus = [dictionary.doc2bow(text) for text in texts]

  print "Generating model ..."
  model = generate_model(args.model, my_corpus, dictionary, args.num_topics, args.num_iter)
  model.save(model_filename)

# kl = arun(my_corpus,dictionary,max_topics=100)

# Plot kl divergence against number of topics
# plt.plot(kl)
# plt.ylabel('Symmetric KL Divergence')
# plt.xlabel('Number of Topics')
# plt.savefig('kldiv.png', bbox_inches='tight')
show_topics(args.model, model, args.num_topics, args.num_top_words)