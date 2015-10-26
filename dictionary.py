import re
import os
import random

class Dictionary(object):
    def __init__(self, filename, name=None, include="^[a-z]+$", weighting=1):
        self.filename = filename
        if name is None:
            self.name = self.filename
        else:
            self.name = name
        self.weighting = weighting
        self.re_include = re.compile(include)
        self.words = self.get_words(self.filename)
        
    def get_words(self, word_file):
        if not os.path.isfile(word_file):
            raise IOError("Could not find word file: " + word_file)

        words = []
        f = open(word_file)
        for line in f:
            # We only want words at least 5 letters long (> 5 including the \n)
            if self.re_include.search(line) and len(line) > 5:
                words.append(line.replace("\n", ""))
                
        return words
        
    def get_random_word(self):
        x = random.randint(0, len(self.words) - 1)
        return self.words[x]
        
    def size(self):
        return len(self.words)

