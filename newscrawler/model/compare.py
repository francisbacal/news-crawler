class Compare:
  """
  Compare Module which checks for content relativity using trigram algorithm.
  """
  def __init__(self, words_list=[]):
    self.inputs = words_list
    self.words = []
    self.word_trigram_count = []
    self.trigrams = {}
    self.trigrams_count = []
    self.trigrams_matches = 0

    i = 0
    while i < len(self.inputs):
      self.__set(self.inputs[i])
      i += 1

  #Callback function to split word to trigram
  def __to_trigram(self, word, _callback = None):
    data = ("  " + word + "  ").upper()
    for i in range(len(data)-1):
      if (_callback and len(data[i:i+3]) == 3):
        _callback(data[i:i+3])

  # Instantiate Compare
  def __set(self, word):
    if (word == None or word == "" or word in self.words):
      pass
    self.trigrams_count.append(0)
    self.words.append(word)
    self.word_trigram_count.append(0)
    word_index = len(self.words) - 1

    def callback(arg):
      try:
        words_for_trigram = self.trigrams[arg]
      except:
        words_for_trigram = []

      if word_index not in words_for_trigram:
        words_for_trigram.append(word_index)
      
      #store trigram and add count
      self.trigrams[arg] = words_for_trigram
      self.word_trigram_count[word_index] += 1
    
    self.__to_trigram(word, callback)


  def eval(self, word, _callback = None):
    """
    Evaluate word or phrase
    """
    # print('\nEvaluating parameter: {}'.format(word.upper()))
    result = []
    word_matches = []
    self.trigrams_matches = 0

    for i in range(len(self.words)):
      word_matches.append(0)

    def callback(arg):
      
      try:
        words_for_trigram = self.trigrams[arg]
        self.trigrams_matches += 1 

        for i in range(len(words_for_trigram)):
          word_index = words_for_trigram[i]
          self.trigrams_count[word_index] += 1

          if word_matches[word_index] is None:
            word_matches[word_index] = 0
          
          word_matches[word_index] += 1
      except:
        pass
    
    self.__to_trigram(word, callback)    

    for i in range(len(self.trigrams_count)):
      count = self.word_trigram_count[i]
      percentage = (word_matches[i]/ count) * 100
      similarity = str(round(percentage)) + "%"

      if percentage >= 49:
        result.append({'word': self.words[i], 'matches': word_matches[i], 'similarity': similarity})
        
    # print("\nThis is the result: {}".format(result))
    return sorted(result, key = lambda i: i['matches'],reverse=True)