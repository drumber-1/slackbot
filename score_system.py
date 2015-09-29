import os
import json

import command_system
import utils

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
        
        self.leader_emoji = ":crown:"
        self.trailer_emoji = ":poop:"

        self.command_system.add_command("score", self.say_score, "Show current scores")
        self.command_system.add_command("points", self.say_system, "Show scoring system")

    def give_points(self, user, points):
        user_id = user.id
        self.users[user_id]["score"] += points

    def add_user(self, id, name):
        if not id in self.users:
            self.users[id] = self.create_user(name)

    def create_user(self, name):
        user = {"score": 0, "name": name}
        return user
        
    def get_user_score_string(self, user_id):
    	return str(self.users[user_id]["name"]) + ": " + str(self.users[user_id]["score"])
        
    def effective_points(self, user_id):
    	return self.users[user_id]["score"]
        
    def sorted_user_ids(self):
    	sorted_ids = sorted(self.users.keys(), key=self.effective_points, reverse=True)
    	return sorted_ids

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
        
        sorted_ids = self.sorted_user_ids()
        
        for k in sorted_ids:
            emoji = ""
            if k is sorted_ids[0]:
        		emoji = self.leader_emoji
            elif k is sorted_ids[-1]:
        		emoji = self.trailer_emoji
            message += "\t" + emoji + " " + self.get_user_score_string(k) + "\n"
        self.say(message)

    def say_system(self):
        message = "Current scoring system:\n"
        if self.points_hit != 0:
            message += "\tCorrect letter: " + str(self.points_hit) + "\n"
        if self.points_miss != 0:
            message += "\tIncorrect letter: " + str(self.points_miss) + "\n"
        if self.points_win != 0:
            message += "\tGame win: " + str(self.points_win) + "\n"
        if self.points_loss != 0:
            message += "\tGame loss: " + str(self.points_loss) + "\n"
        self.say(message)

    def save_to_state(self):
        save_state = {}
        save_state["users"] = self.users
        return save_state

    def load_from_state(self, save_state):
        self.users = save_state["users"]
        for k in self.users.keys():
            self.update_user(self.users[k])

    def save_to_file(self, fname):
        fout = open(fname, 'w')
        json.dump(self.save_to_state(), fout, indent=4)

    def load_from_file(self, fname):
        if not os.path.isfile(fname):
            return

        fin = open(fname, 'r')
        save_state = json.load(fin)
        self.load_from_state(save_state)



class DifficultyScoringSystem(BasicScoreSystem):
    def __init__(self, hangman, output_funct):
        super(DifficultyScoringSystem, self).__init__(hangman, output_funct)

        self.difficulty = 0
        self.difficulty_max = 5
        self.difficulty_strings = ["E-zed mode", "Not-so-e-zed Mode", "Come Get Some", "Legendary", "Nightmare",
                                   "MAXIMUM OVER-BUSINESS"]
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

    def say_stats(self, slack_user):
        if slack_user.id not in self.users:
            self.say("Who are you? Type \"hm: join\" to join!")
            return
        message = "Stats for " + slack_user.name + ":\n"

        message += "\nScore:\t" + str(self.users[slack_user.id]["score"])

        message += "\nWins / Loses:\n"
        for i in range(0, self.difficulty_max + 1):
            wins = self.users[slack_user.id]["wins"][i]
            loses = self.users[slack_user.id]["loses"][i]
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

    def save_to_state(self):
        save_state = super(DifficultyScoringSystem, self).save_to_state()
        save_state["difficulty"] = self.difficulty
        return save_state

    def load_from_state(self, save_state):
        super(DifficultyScoringSystem, self).load_from_state(save_state)
        self.set_difficulty(int(save_state["difficulty"]))


class StealingScoringSystem(DifficultyScoringSystem):
    def __init__(self, hangman, output_funct):
        super(StealingScoringSystem, self).__init__(hangman, output_funct)

        self.difficulty_points_hit = [1, 2, 3, 4, 5, 6]
        self.difficulty_points_miss = [-1, -2, -3, -4, -5, -6]
        self.difficulty_points_win = [0, 0, 0, 0, 0, 0]
        self.difficulty_points_loss = [0, 0, 0, 0, 0, 0]
        self.difficulty_points_win_steal = [10, 20, 30, 40, 50, 60]
        self.points_win_steal = 10

        self.steal_responses = utils.read_responses("hangman_strings/steal")
        self.invalid_steal_responses = utils.read_responses("hangman_strings/invalidsteal")

        self.command_system.add_command("steal", self.steal, "Take what is rightfully yours", requires_user=True,
                                        has_args=True)

    def create_user(self, name):
        user = {"score": 0,
                "name": name,
                "wins": [0, 0, 0, 0, 0, 0],
                "loses": [0, 0, 0, 0, 0, 0],
                "credit": 0,
                "stolenpoints": 0}
        return user
        
    def get_user_score_string(self, user_id):
    	ret = super(StealingScoringSystem, self).get_user_score_string(user_id)
    	if self.users[user_id]["credit"] != 0:
    		ret += " (+" + str(self.users[user_id]["credit"]) + " to steal)"
    	return ret
        
    def effective_points(self, user_id):
    	return self.users[user_id]["score"] + self.users[user_id]["credit"]

    def score_win_game(self, slack_user):
        potential_credit = self.points_win_steal
        super(StealingScoringSystem, self).score_win_game(slack_user)
        if slack_user.id == self.sorted_user_ids()[0]:
        	self.users[slack_user.id]["score"] += potential_credit
        	message = "{user} gets {points} points for winning!"
        	self.say(message.format(user=slack_user.name, points=potential_credit))
        else:
        	self.users[slack_user.id]["credit"] += potential_credit
        	message = "{user} may now say \"hm: steal <victim>\", to take {credit} points from them!"
        	self.say(message.format(user=slack_user.name, credit=self.users[slack_user.id]["credit"]))

    def set_difficulty(self, new_difficulty):
        super(StealingScoringSystem, self).set_difficulty(new_difficulty)
        self.points_win_steal = self.difficulty_points_win_steal[self.difficulty]

    def steal(self, slack_user, args):
        if slack_user.id not in self.users:
            self.say("Who are you? Type \"hm: join\" to join!")
            return

        if self.users[slack_user.id]["credit"] == 0:
            self.say(utils.randomelement(self.invalid_steal_responses).format(user=slack_user.name))
            return

        if len(args) == 0:
            self.say("You must name your target")
            return

        target_username = args[0].lower()

        if target_username == "hangmanbot":
            self.say("Nice try")
            return

        if target_username == slack_user.name:
            self.say("You steal from yourself. You gain nothing. You idiot.")
            self.users[slack_user.id]["credit"] = 0
            return

        target_user = None
        for u in self.users.values():
            if u["name"] == target_username:
                target_user = u

        if target_user is None:
            self.say("Who the hell is \"" + str(target_username) + "\"?")
            return

        target_user["score"] -= self.users[slack_user.id]["credit"]
        target_user["stolenpoints"] += self.users[slack_user.id]["credit"]
        self.users[slack_user.id]["score"] += self.users[slack_user.id]["credit"]
        self.users[slack_user.id]["credit"] = 0

        self.say(utils.randomelement(self.steal_responses).format(user=target_user["name"]))
        self.say_score()

    def say_system(self):
        super(StealingScoringSystem, self).say_system()
        message = "\n"
        message += "Winning grants you " + str(self.points_win_steal) + " points\n"
        message += "If you are not in the lead you may steal these points from a victim of your choosing!"
        self.say(message)

    def say_stats(self, slack_user):
        super(StealingScoringSystem, self).say_stats(slack_user)
        message = "\nStolen points:\t" + str(self.users[slack_user.id]["stolenpoints"])
        self.say(message)

    def say_score(self):
        super(StealingScoringSystem, self).say_score()
        message = "\n"
        for u in self.users.values():
            if u["credit"] > 0:
                message += str(u["name"]) + " has " + str(u["credit"]) + " points to steal\n"
        self.say(message)
