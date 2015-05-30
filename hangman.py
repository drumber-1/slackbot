import random
import re
import os

class Hangman(object):
	def __init__(self, word_file):
		self.game_state = "ready"
		self.word = ""
		self.words = []
		self.re_include = re.compile("^[a-z]+$")
		self.blank_char = "-"
		self.letters_missed = ""
		self.letters_guessed = ""
		self.started = False
		self.difficulty = 0
		self.difficulty_current = 0  # Increasing the difficulty will only take place for the next game
		# This is fudged for slacks text formatting
		# which is not monospaced for multiple spaces
		self.state_prefix = "+---+\n"
		self.state_suffix = "|\n==========\n"
		self.states = ["|       |\n|        \n|         \n|         \n",
					   "|       |\n|       0\n|         \n|         \n",
					   "|       |\n|       0\n|       | \n|         \n",
					   "|       |\n|       0\n|     /|  \n|         \n",
					   "|       |\n|       0\n|     /|\ \n|         \n",
					   "|       |\n|       0\n|     /|\ \n|     /   \n",
					   "|       |\n|       0\n|     /|\ \n|     / \ \n"]

		self.generate_words(word_file)

	def start(self):
		self.word = self.get_random_word()
		print("(hangman) " + self.word)
		self.letters_missed = ""
		self.letters_guessed = ""
		self.started = True
		self.difficulty_current = self.difficulty
		self.game_state = "started"

	def get_state_string(self):
		n = min(self.get_state(), len(self.states) - 1)
		return self.state_prefix + self.states[n] + self.state_suffix

	def get_word_string(self):
		s = ""
		for c in self.word:
			if c in self.letters_guessed:
				s += c
			else:
				s += self.blank_char
		return s

	def get_state(self):
		return len(self.letters_missed) + self.difficulty_current

	def set_difficulty(self, new_difficulty):
		if new_difficulty < 0:
			print("(hangman) Cannot set difficulty to " + str(new_difficulty) + " (min 0)")
			return
		if new_difficulty > (len(self.states) - 1):
			print("(hangman) Cannot set difficulty to " + str(new_difficulty) + " (max " + str(len(self.states) - 1) + ")")
			return
		self.difficulty = new_difficulty

	def guess(self, c):
		if not self.game_state == "started":
			return "invalid"

		if (not self.re_include.search(c)) or len(c) > 1:
			return "invalid"
		if c in self.letters_guessed or c in self.letters_missed:
			return "repeat"
		if c in self.word:
			self.letters_guessed += c
			if self.blank_char not in self.get_word_string():
				self.game_state = "win"
			return "hit"
		else:
			self.letters_missed += c
			if self.get_state() == (len(self.states) - 1):
				self.game_state = "lose"
			return "miss"

	def generate_words(self, word_file):
		if not os.path.isfile(word_file):
			raise IOError("Could not find word file: " + word_file)

		self.words = []
		f = open(word_file)
		for line in f:
			# We only want words at least 5 letters long (> 5 including the \n)
			if self.re_include.search(line) and len(line) > 5:
				self.words.append(line.replace("\n", ""))
			else:
				continue

	def get_random_word(self):
		x = random.randint(0, len(self.words) - 1)
		return self.words[x]
