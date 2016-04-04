import re
import os
from stop_words import get_stop_words


dir = os.getcwd()
model_dir = os.path.join(dir, 'models/')
dataset_dir = os.path.join(dir, 'datasets/')
dictionary_dir = os.path.join(dir, 'dictionaries/')
executable_dir = os.path.join(dir, 'executables/')

en_stop = get_stop_words('en')


_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))


def get_dict_dir(s):
  return os.path.join(dictionary_dir, s)

def get_exec_dir(s):
  return os.path.join(executable_dir, s)


# Or using the /usr/share/dict/british-english word list


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

