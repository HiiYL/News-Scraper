import os
import re


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

def show_topics(model_type, model, num_topics, num_top_words):
  if model_type == "lda" :
    for topic in model.show_topics(num_topics=num_topics, num_words=int(num_top_words), log=False, formatted=False):
      print "Topic #" + str(topic[0]) + " :",
      for word in topic[1]:
        print word[0],
      print
  elif model_type == "dtm" :
    for idx, topic in enumerate(model.show_topics(topics=num_topics, topn=int(num_top_words),times=1, formatted=False)):
      print "Topic #" + str(idx) + " :",
      for word in topic:
        print word[1],
      print
  else:
    print "Uh-oh unknown model detected, fix me at utils.py"

def get_model_with_arguments_filename(args):
  return (args.filename.split('.')[0] + "_" + args.stemmer + "_" + args.num_iter +
   "_" + args.num_top_words + "_" + args.num_topics  + "_" + args.model + "_" + args.dictionary)