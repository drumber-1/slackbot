import random
import utils

default_code = {
"a" : [u"\U0001D5BA", u"\u0430"],
##"b" : [u"\U0001D68B"],
"c" : [u"\u0441"],
"d" : [u"\u217E"],
"e" : [u"\u0435"],
##"f" : [u"\U0001D41F"],
##"g" : [u"\U0001D420"],
"h" : [u"\u0570"],
"i" : [u"\u0456"],
##"j" : [u"\u0458"],
##"k" : [u"\U0001D694"],
##"l" : [u"\U0001D425"],
##"m" : [u"\U0001D5C6"],
"n" : [u"\u0578"],
"o" : [u"\u043E", u"\u03BF", u"\u0585"],
"p" : [u"\u0440"],
"q" : [u"\u051B"],
##"r" : [u"\U0001D42B"],
"s" : [u"\u0455"],
"t" : [u"\U0001D5CD"],
"u" : [u"\u057D"],
"v" : [u"\u2174"],
"w" : [u"\u051D"],
"x" : [u"\u0445"],
"y" : [u"\u0443"],
"z" : [u"\u1D22"],
}

class LetterSwitcher(object):
	def __init__(self, code=default_code, chance=0.1):
		self.code = code
		self.switch_chance = chance
		
	def process_letter(self, letter):
		if letter in self.code:
			if random.random() <= self.switch_chance:
				return utils.randomelement(self.code[letter])
		return letter		
		
	# fix_transform will transform all letters the same, to reduce suspicion 
	def process_word(self, word, fix_transform=True):
		processed_word = ""
		previous_transforms = {}
		for l in word:
			if fix_transform and l in previous_transforms:
				processed_word += previous_transforms[l]
			else:
				new_letter = self.process_letter(l)
				processed_word += new_letter
				previous_transforms[l] = new_letter
			
		return processed_word
