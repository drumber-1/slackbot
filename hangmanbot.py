import basics
import hangman
import random
import score_system

scorefile = "scores.json"

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
		self.add_command("show", self.display, "Show the current game state")

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
		if self.hm.game_state == "started":
			self.saypush("A game has already been started you dingus\n")
		else:
			self.hm.start()
			self.say("Game started!\n")
			self.display()

	def unknown_command(self, user, cmd):
		if len(cmd[0]) == 1:
			self.make_guess(user, cmd[0])
		else:
			self.saypush(randomelement(self.unknown))

	def make_guess(self, user, letter):
		if not self.hm.game_state == "started":
			self.saypush("No game in progress, say \"hm: start\" to start one!\n")
			return
		ret = self.hm.guess(letter)
		if ret == "invalid":
			self.saypush(letter + " is not a valid guess.\n")
		elif ret == "repeat":
			self.saypush("Someone already guessed " + letter + "\n")
		elif ret == "hit":
			self.saypush(randomelement(self.hit))
			self.score_system.score_correct_guess(user)
			self.turn_end(user)
		elif ret == "miss":
			self.saypush(randomelement(self.miss))
			self.score_system.score_incorrect_guess(user)
			self.turn_end(user)
		return

	# Perform common actions at end of turn
	def turn_end(self, user):
		if self.hm.game_state == "win":
			self.score_system.score_win_game(user)
		elif self.hm.game_state == "lose":
			self.score_system.score_lose_game(user)

		self.score_system.save_game(scorefile)
		self.display()
