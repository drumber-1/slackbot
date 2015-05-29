import os
import json

def default_user():
	user = {"score": 0}
	return user


class BasicScoreSystem(object):
	def __init__(self, hangman):
		self.users = {}
		self.hm = hangman

	def give_points(self, user, points):
		if user not in self.users.keys():
			self.users[user] = default_user()

		self.users[user]["score"] += points

	def score_correct_guess(self, user):
		self.give_points(user, 1)

	def score_incorrect_guess(self, user):
		self.give_points(user, -2)

	def score_win_game(self, user):
		self.give_points(user, max(15 - len(self.hm.word), 5))

	def score_lose_game(self, user):
		pass

	def get_score_string(self):
		message = "Current scores:\n"
		for k in self.users.keys():
			message += "\t" + k + ": " + str(self.users[k].score) + "\n"
		message += "\tEVERYONE ELSE: ZERO\n"
		return message

	def get_system_string(self):
		message = "Current scoring system:\n"
		message += "\tCorrect letter: +1\n"
		message += "\tIncorrect letter: -2\n"
		message += "\tGame win: +(15 - word length) (min 5)\n"
		return message

	def save_game(self, fname):
		fout = open(fname, 'w')
		json.dump(self.users, fout)

	def load_game(self, fname):
		if not os.path.isfile(fname):
			return

		self.users = {}
		fin = open(fname, 'r')
		self.users = json.load(fin)