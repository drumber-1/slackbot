import basics
import hangman
import random
import score_system

scorefile = "scores.txt"

def randomelement(elements):
	return elements[random.randint(0, len(elements) - 1)]

def read_responses(fname):
	responses = []
	f = open(fname)
	for line in f:
		responses.append(line)
	return responses		

class HangmanBot(basics.BasicBot):
	def __init__(self, channel):
		super(HangmanBot, self).__init__("HangmanBot", "hm", channel, avatar="http://imgur.com/juZ7nAC.jpg", descripton="A bot for playing hangman!")
		self.hm = hangman.Hangman("./words.txt")
		# self.hm = hangman.Hangman("/usr/share/dict/words")
		
		self.agress = read_responses("hangman_strings/agress")
		self.hit = read_responses("hangman_strings/hit")
		self.miss = read_responses("hangman_strings/miss")
		self.unknown = read_responses("hangman_strings/unknown")
		self.jeopardy = read_responses("hangman_strings/jeopardy")

		self.add_command("start", self.game_start, "Start a new game")

		self.score_system = score_system.BasicScoreSystem(self.hm)
		self.score_system.load_game(scorefile)
		
	def display(self):
		if self.hm.game_state == "ready":
			self.saypush("No game in progress, say \"hm: start\" to start one!")
			return
			
		self.say(self.hm.get_state_string() + "\n")
		self.say("Word: " + self.hm.get_word_string() + "\n")
		self.say("Letters missed: " + self.hm.letters_missed + "\n")
		self.say("Letters guessed: " + self.hm.letters_guessed + "\n")
			
		if self.hm.game_state == "win":
			self.say("\n")
			self.say("Humans win!\n")
			self.say("Say \"hm: start\" to start a new game!")
		elif self.hm.game_state == "lose":
			self.say("\n")
			self.say("Humans lose!\n")
			self.say("The word was " + self.hm.word + "\n")
			self.say("Say \"hm: start\" to start a new game!")
			
		self.push()

	def game_start(self):
		self.hm.start()
		self.say("Game started!\n")
		self.display()

	# Perform common actions at end of turn
	def turn_end(self, user):
		self.score_system.save_game(scorefile)
		self.display()
	
	# Perform clean up actions at end of game
	def game_end(self):
		self.users_jeopardy = []
		return
