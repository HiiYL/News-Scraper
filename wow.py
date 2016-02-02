import numpy as np
import lda
import lda.datasets
import csv
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim
import sys

reload(sys)
sys.setdefaultencoding('utf8')

tokenizer = RegexpTokenizer(r'\w+')
en_stop = get_stop_words('en')
p_stemmer = PorterStemmer()
f = open("soya_20160202.csv")
reader = csv.reader(f)
csv_length = sum(1 for row in reader)
f.seek(0) #reset reader position

contents = [ row[6] for row in reader ]
texts = list()
for idx,i in enumerate(contents):
  print idx
  # clean and tokenize document string
  raw = i.lower()
  tokens = tokenizer.tokenize(raw)
  # remove stop words from tokens
  stopped_tokens = [i for i in tokens if not i in en_stop]
  texts.append(stopped_tokens)

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

X = np.zeros((len(corpus), len(dictionary)), dtype=np.int)
for idx,i in enumerate(corpus):
  for j in i:
    X[idx][j[0]] = j[1]
model = lda.LDA(n_topics=20, n_iter=1500, random_state=1)
model.fit(X)
n_top_words = 8
topic_word = model.topic_word_  # model.components_ also works
for i, topic_dist in enumerate(topic_word):
  topic_words = [ dictionary[x] for x in np.array(dictionary)[np.argsort(topic_dist)][:-(n_top_words+1):-1] ]
  print('Topic {}: {}'.format(i, ' '.join(topic_words)))