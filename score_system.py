import os
import json
import command_system

class BasicScoreSystem(object):
	def __init__(self, hangman, output_funct):
		self.users = {}
		self.hm = hangman
		self.command_system = command_system.CommandSystem()
		self.say = output_funct

		self.points_hit = 1
		self.points_miss = -2
		self.points_win = 10
		self.points_loss = 0

		self.command_system.add_command("score", self.say_score, "Show current scores")
		self.command_system.add_command("points", self.say_system, "Show scoring system")

	def give_points(self, user, points):
		user_id = user["id"]
		if user_id not in self.users.keys():
			self.users[user_id] = self.create_user(user["name"])
		self.users[user_id]["score"] += points

	def create_user(self, name):
		user = {"score": 0, "name": name}
		return user

	def update_user(self, user):  # If a user is from an old save, fills in missing fields with default values
		default_user = self.create_user("a name")
		for k in default_user.keys():
			if k not in user:
				user[k] = default_user[k]

	def score_correct_guess(self, user):
		self.give_points(user, self.points_hit)

	def score_incorrect_guess(self, user):
		self.give_points(user, self.points_miss)

	def score_win_game(self, user):
		self.give_points(user, self.points_win)

	def score_lose_game(self, user):
		self.give_points(user, self.points_loss)

	def say_score(self):
		message = "Current scores:\n"
		for k in self.users.keys():
			message += "\t" + str(self.users[k]["name"]) + ": " + str(self.users[k]["score"]) + "\n"
		message += "\tEVERYONE ELSE: ZERO\n"
		self.say(message)

	def say_system(self):
		message = "Current scoring system:\n"
		message += "\tCorrect letter: " + str(self.points_hit) + "\n"
		message += "\tIncorrect letter: " + str(self.points_miss) + "\n"
		message += "\tGame win: " + str(self.points_win) + "\n"
		message += "\tGame loss: " + str(self.points_loss) + "\n"
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
		for k in self.users.keys():
			self.update_user(self.users[k])

class DifficultyScoringSystem(BasicScoreSystem):
	def __init__(self, hangman, output_funct):
		super(DifficultyScoringSystem, self).__init__(hangman, output_funct)

		self.difficulty = 0
		self.difficulty_max = 5
		self.difficulty_strings = ["E-zed mode", "Not-so-e-zed Mode", "Come Get Some", "Legendary", "Nightmare", "MAXIMUM OVER-BUSINESS"]
		self.difficulty_points_hit = [1, 2, 3, 4, 5, 6]
		self.difficulty_points_miss = [-2, -4, -9, -16, -25, -36]
		self.difficulty_points_win = [10, 20, 30, 40, 50, 60]
		self.difficulty_points_loss = [0, 0, 0, 0, 0, 0]
		self.win_streak = 0
		self.loss_streak = 0
		self.wins_per_inc = 2
		self.loses_per_dec = 1

		self.command_system.add_command("difficulty", self.say_difficulty_message, "Show current difficulty")
		self.command_system.add_command("stats", self.say_stats, "Show your stats", requires_user=True)

	def create_user(self, name):
		user = {"score": 0, "name": name, "wins": [0, 0, 0, 0, 0, 0]}
		return user

	def n_guesses(self):
		return self.difficulty_max - self.difficulty + 1

	def say_difficulty_message(self):
		message = ""
		message += "*" * self.difficulty
		message += " " + self.difficulty_strings[self.difficulty] + " "
		message += "*" * self.difficulty
		message += "\n"
		message += "("
		if self.n_guesses() == 1:
			message += str(self.n_guesses()) + " guess)\n"
		else:
			message += str(self.n_guesses()) + " guesses)\n"
		self.say(message)

	def say_stats(self, user):
		if user["id"] not in self.users:
			self.say("You have no stats! Play some games first!")
			return
		message = "Stats for " + user["name"] + ":\n\n"
		message += "Wins:\n"
		for i in range(0, self.difficulty_max + 1):
			wins = self.users[user["id"]]["wins"][i]
			if wins == 0:
				message += "\tDifficulty " + str(i)
			else:
				message += "\tDifficulty " + str(self.difficulty_strings[i])
			message += ": " + str(self.users[user["id"]]["wins"][i]) + "\n"
		self.say(message)

	def change_difficulty(self, dir):
		if dir == "up":
			if self.difficulty == self.difficulty_max - 1:
				self.say("Difficulty has already reached maximum!")
				return
			self.say("Difficulty increased!\n")
			self.set_difficulty(self.difficulty + 1)
		elif dir == "down":
			if self.difficulty == 0:
				self.say("The game is already as easy as I can make it!")
				return
			self.say("Difficulty decreased!\n")
			self.set_difficulty(self.difficulty - 1)
		self.say_difficulty_message()

	def set_difficulty(self, new_difficulty):
		self.difficulty = new_difficulty
		self.hm.set_difficulty(new_difficulty)
		self.points_hit = self.difficulty_points_hit[self.difficulty]
		self.points_miss = self.difficulty_points_miss[self.difficulty]
		self.points_win = self.difficulty_points_win[self.difficulty]
		self.points_loss = self.difficulty_points_loss[self.difficulty]

	def score_win_game(self, user):
		super(DifficultyScoringSystem, self).score_win_game(user)
		self.users[user["id"]]["wins"][self.difficulty] += 1
		self.win_streak += 1
		self.loss_streak = 0
		if self.win_streak >= self.wins_per_inc:
			self.change_difficulty("up")
			self.win_streak = 0

	def score_lose_game(self, user):
		super(DifficultyScoringSystem, self).score_lose_game(user)
		self.loss_streak += 1
		self.win_streak = 0
		if self.loss_streak >= self.loses_per_dec:
			self.change_difficulty("down")
			self.loss_streak = 0

	def say_score(self):
		super(DifficultyScoringSystem, self).say_score()

	def say_system(self):
		super(DifficultyScoringSystem, self).say_system()
		message = "\n"
		message += "Winning " + str(self.wins_per_inc) + " in a row will remove one guess\n"
		message += "Losing " + str(self.loses_per_dec) + " in a row will return one guess\n"
		message += "Higher difficulties give (and take away) more points!\n"
		self.say(message)

	def save_game(self, fname):
		fout = open(fname, 'w')
		users_json = json.dumps(self.users)
		fout.write(users_json)
		fout.write("\n")
		fout.write(str(self.difficulty))

	def load_game(self, fname):
		if not os.path.isfile(fname):
			return

		self.users = {}
		fin = open(fname, 'r')
		users_json_string = fin.readline()
		self.users = json.loads(users_json_string)
		for k in self.users.keys():
			self.update_user(self.users[k])
		diff_string = fin.readline()
		self.set_difficulty(int(diff_string))



