import os
import json
import command_system

class BasicScoreSystem(object):
	def __init__(self, hangman, output_funct):
		self.users = {}
		self.hm = hangman
		self.command_system = command_system.CommandSystem()
		self.say = output_funct

		self.command_system.add_command("score", self.say_score, "Show the current scores")
		self.command_system.add_command("points", self.say_system, "Show the scoring system")

	def give_points(self, user, points):
		user_id = user["id"]
		if user_id not in self.users.keys():
			self.users[user_id] = self.create_user(user["name"])
		self.users[user_id]["score"] += points

	def create_user(self, name):
		user = {"score": 0, "name": name}
		return user

	def score_correct_guess(self, user):
		self.give_points(user, 1)

	def score_incorrect_guess(self, user):
		self.give_points(user, -2)

	def score_win_game(self, user):
		self.give_points(user, max(15 - len(self.hm.word), 5))

	def score_lose_game(self, user):
		pass

	def say_score(self):
		message = "Current scores:\n"
		for k in self.users.keys():
			message += "\t" + str(self.users[k]["name"]) + ": " + str(self.users[k]["score"]) + "\n"
		message += "\tEVERYONE ELSE: ZERO\n"
		self.say(message)

	def say_system(self):
		message = "Current scoring system:\n"
		message += "\tCorrect letter: +1\n"
		message += "\tIncorrect letter: -2\n"
		message += "\tGame win: +(15 - word length) (min 5)\n"
		self.say(message)

	def save_game(self, fname):
		fout = open(fname, 'w')
		json.dump(self.users, fout)

	def load_game(self, fname):
		if not os.path.isfile(fname):
			return

		self.users = {}
		fin = open(fname, 'r')
		self.users = json.load(fin)
