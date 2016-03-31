_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))


def get_dict_dir(s):
  return os.path.join(dictionary_dir, s)

def get_exec_dir(s):
  return os.path.join(executable_dir, s)


# Or using the /usr/share/dict/british-english word list
if args.dictionary == "none":
  def is_english_word(word):
    return true
elif args.dictionary == "english":
  d = enchant.Dict("en_US")
  def is_english_word(word):
    return d.check(word)
else:
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
   "_" + args.num_top_words + "_" + args.num_topics  + "_" + args.model + "_" + args.dictionary)