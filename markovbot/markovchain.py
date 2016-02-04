import pickle
import random

class MarkovChain(object):
    def __init__(self, word_grouping=2, min_sentence_length=4):
        self.chain = {}
        self.parsed_words = 0
        self.parsed_messages = 0
        self.word_grouping = word_grouping
        self.min_sentence_length = min_sentence_length

        self.start_index = "START"
        self.end_index = "END"

    def get_groups(self, words):
        words = [self.start_index] + words + [self.end_index]

        if len(words) < self.word_grouping:
            return

        for i in range(len(words) - (self.word_grouping - 1)):
            yield (words[i:i+self.word_grouping])

    def add_message(self, message):
        words = message.split()
        if len(words) < self.min_sentence_length:
            return False
        self.parsed_messages += 1
        self.parsed_words += len(words)

        groups = self.get_groups(words)
        first = True
        for group in groups:
            if first:
                self.add_to_chain(self.start_index, tuple(group[1:]))
                first = False
            key = tuple(group[:len(group) - 1])
            value = group[-1]
            self.add_to_chain(key, value)
            
        return True

    def add_to_chain(self, key, value):
        if key in self.chain:
            self.chain[key].append(value)
        else:
            self.chain[key] = [value]

    def generate_text(self, max_length=25):
    	if self.start_index not in self.chain:
    		return ""
        generated_text = []

        test_group = random.choice(self.chain[self.start_index])
        if test_group[-1] == self.end_index:
            generated_text += list(test_group[:len(test_group) - 1])
            return ' '.join(generated_text)
        else:
            generated_text += list(test_group)

        last_end = 0
        for i in range(max_length):
            possible_words = self.chain[test_group]
            if self.end_index in possible_words:
                last_end = i

            word = random.choice(self.chain[test_group])
            if word == self.end_index:
                break
            generated_text.append(word)
            test_group = test_group[1:] + (word,)

        generated_text = generated_text[:last_end + self.word_grouping - 1]
        return ' '.join(generated_text)
        
    def get_join_freq(self):
    	freq = {}
    	for k in self.chain.keys():
    		njoins = len(self.chain[k])
    		if njoins in freq:
    			freq[njoins] += 1
    		else:
    			freq[njoins] = 1
    	return freq
    	
    def print_freq(self):
    	freq = self.get_join_freq()
    	print "njoins", "freq"
    	for njoins in freq.keys():
    		print njoins, freq[njoins]
        
    def save(self, filename):
    	f = open(filename, 'wb')
    	pickle.dump(self.chain, f, 2)
    	f.close()
    	
    def load(self, filename):
    	f = open(filename, 'rb')
    	self.chain = pickle.load(f)
