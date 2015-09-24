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
		user_id = user.id
		if user_id not in self.users.keys():
			self.users[user_id] = self.create_user(user.name)
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
		
		save_state = {}
		save_state["users"] = self.users
		json.dump(save_state, fout)

	def load_game(self, fname):
		if not os.path.isfile(fname):
			return

		fin = open(fname, 'r')
		save_state = json.load(fin)
		self.users = save_state["users"]
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
		user = {"score": 0,
		        "name": name,
		        "wins": [0, 0, 0, 0, 0, 0],
		        "loses": [0, 0, 0, 0, 0, 0]}
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
		if user.id not in self.users:
			self.say("You have no stats! Play some games first!")
			return
		message = "Stats for " + user.name + ":\n"
		
		message += "\nScore:\n"
		message += "\t" + self.users[user.id]["score"]
		
		message += "\nWins / Loses:\n"
		for i in range(0, self.difficulty_max + 1):
			wins = self.users[user.id]["wins"][i]
			loses = self.users[user.id]["loses"][i]
			if wins == 0:
				message += "\tDifficulty " + str(i)
			else:
				message += "\t" + str(self.difficulty_strings[i])
			message += ": " + str(wins) + " / " + str(loses) + "\n"
		self.say(message)

	def change_difficulty(self, dir):
		if dir == "up":
			if self.difficulty == self.difficulty_max:
				self.say("No more difficulty levels! You win I guess?")
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
		self.users[user.id]["wins"][self.difficulty] += 1
		self.win_streak += 1
		self.loss_streak = 0
		if self.win_streak >= self.wins_per_inc:
			self.change_difficulty("up")
			self.win_streak = 0

	def score_lose_game(self, user):
		super(DifficultyScoringSystem, self).score_lose_game(user)
		self.users[user.id]["loses"][self.difficulty] += 1
		self.loss_streak += 1
		self.win_streak = 0
		if self.loss_streak >= self.loses_per_dec:
			self.change_difficulty("down")
			self.loss_streak = 0

	def say_system(self):
		super(DifficultyScoringSystem, self).say_system()
		message = "\n"
		message += "Winning " + str(self.wins_per_inc) + " in a row will remove one guess\n"
		message += "Losing " + str(self.loses_per_dec) + " in a row will return one guess\n"
		message += "Higher difficulties give (and take away) more points!\n"
		self.say(message)

	def save_game(self, fname):
		fout = open(fname, 'w')
		
		save_state = {}
		save_state["users"] = self.users
		save_state["difficulty"] = self.difficulty
		json.dump(save_state, fout)

	def load_game(self, fname):
		if not os.path.isfile(fname):
				return

		fin = open(fname, 'r')
		save_state = json.load(fin)
		self.users = save_state["users"]
		self.set_difficulty(int(save_state["difficulty"]))
		
		for k in self.users.keys():
			self.update_user(self.users[k])

class StealingScoringSystem(DifficultyScoringSystem):
	def __init__(self, hangman, output_funct):
		super(StealingScoringSystem, self).__init__(hangman, output_funct)
		
		self.difficulty_points_hit = [1, 2, 3, 4, 5, 6]
		self.difficulty_points_miss = [-1, -2, -3, -4, -5, -6]
		self.difficulty_points_win = [0, 0, 0, 0, 0, 0]
		self.difficulty_points_loss = [0, 0, 0, 0, 0, 0]
		self.difficulty_points_win_steal = [10, 20, 30, 40, 50, 60]
		self.points_win_steal = 10
		
		self.command_system.add_command("steal", self.steal, "Take what is rightfully yours", requires_user=True, has_args=True)
		
	def create_user(self, name):
		user = {"score": 0,
		        "name": name,
		        "wins": [0, 0, 0, 0, 0, 0],
		        "loses": [0, 0, 0, 0, 0, 0],
		        "credit": 0}
		return user
		
	def score_win_game(self, user):
		super(StealingScoringSystem, self).score_win_game(user)
		self.users[user.id]["credit"] += self.points_win_steal
		
	def set_difficulty(self, new_difficulty):
		super(StealingScoringSystem, self).set_difficulty(new_difficulty)
		self.points_win_steal = self.difficulty_points_win_steal[self.difficulty]
		
	def steal(self, user, target_username)
		target_user = None
		for u in self.users:
			if u["name"] == target_username:
				target_user = u
		
		if target_user == None:
			self.say("Who the hell is " + str(target_username) + " ?")
			return
			
		self.target_user["score"] -= self.users[user.id]["credit"]
		self.users[user.id]["credit"] = 0
	
	def say_system(self):
		super(StealingScoringSystem, self).say_system()
		message = "\n"
		message += "Winning lets you steal " + str(self.points_win_steal) + " from a victim of your choosing!"
		self.say(message)
		
	def say_stats(self, user):
		super(StealingScoringSystem, self).say_stats()
		message = "\nStealing points:"
		message += "\t" + self.users[user.id]["credit"]
		self.say(message)
		
