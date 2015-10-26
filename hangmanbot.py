import commandbot
import hangman
import score_system
import utils
import letterswitcher

class HangmanBot(commandbot.CommandBot):
    def __init__(self, api_key, channel, dictionaries, antibot=True):
        super(HangmanBot, self).__init__(api_key, channel, "hm", description="A bot for playing hangman!")
        self.hm = hangman.Hangman(dictionaries)
        self.ls = letterswitcher.LetterSwitcher()
        
        self.antibot = antibot

        self.agress = utils.read_responses("hangman_strings/agress")
        self.hit = utils.read_responses("hangman_strings/hit")
        self.miss = utils.read_responses("hangman_strings/miss")
        self.unknown = utils.read_responses("hangman_strings/unknown")

        self.swears = ["fuck", "shit", "cunt"]

        self.command_system.add_command("start", self.game_start, "Start a new game")
        self.command_system.add_command("show", self.display, "Show current game state")
        self.command_system.add_command("join", self.add_player, "Join in the fun!", requires_user=True)
        self.command_system.add_command("dictionaries", self.show_dictionaries, "Show which dictionaries are in use")

        # self.score_system = score_system.BasicScoreSystem(self.hm, self.saypush, "scores.json")
        # self.score_system = score_system.DifficultyScoringSystem(self.hm, self.saypush, "scores.json")
        self.score_system = score_system.StealingScoringSystem(self.hm, self.saypush, "scores.json")
        self.score_system.load_from_file()
        self.command_system.sub_command_system = self.score_system.command_system

    def display(self):
        if self.hm.game_state == "ready":
            self.saypush("No game in progress, type \"hm: start\" to start one!")
            return

        self.say("```" + self.hm.get_state_string() + "```\n")
        self.say("Word: ")
        self.say_antibot(self.hm.get_word_string() + "\n")
        self.say("Letters missed: ")
        self.say_antibot(self.hm.letters_missed + "\n")
        self.say("Letters guessed: ")
        self.say_antibot(self.hm.letters_guessed + "\n")

        if self.hm.game_state == "win":
            self.say("\n")
            self.say("Humans win!\n")
            self.say("Type \"hm: start\" to start a new game!")
        elif self.hm.game_state == "lose":
            self.say("\n")
            self.say("Humans lose!\n")
            self.say("The word was " + self.hm.word + "\n")
            self.say("Type \"hm: start\" to start a new game!")

        self.push()
        
    def say_antibot(self, message):
    	if self.antibot:
    		self.say(self.ls.process_word(message))
    	else:
    		self.say(message)
        
    def show_dictionaries(self):
        self.say("Dictionaries in use:\n")
        template = "{dictionary}\n\twords: {words}, weighting: {weighting}\n"
        for d in self.hm.dictionaries:
            self.say(template.format(dictionary=d.name, words=d.size(), weighting=d.weighting))
        self.push()
        
    def add_player(self, slack_user):
        if slack_user.id in self.score_system.users:
            self.saypush("You are already playing stupid\n")
            return
        self.score_system.add_user(slack_user.id, slack_user.name)
        self.saypush("Welcome {user}, type \"hm: start\" to start a game!\n".format(user=slack_user.name))
        

    def game_start(self):
        if self.hm.game_state == "started":
            self.saypush("A game has already been started you dingus\n")
        else:
            dictionary = self.hm.start()
            self.say("Game started!\n")
            template = "The word was selected from the {dictionary} ({words} words)\n"
            self.say(template.format(dictionary=dictionary.name, words=dictionary.size()))
            self.display()

    def runoff_message(self, user, cmd, arguments, message):
        if len(cmd) == 1:
            self.make_guess(user, cmd)
            return True
        else:
            return False

    def unknown_command(self, user, cmd, arguments):
        if self.has_swearing(cmd, arguments):
            self.saypush(utils.randomelement(self.agress))
        else:
            self.saypush(utils.randomelement(self.unknown))

    def has_swearing(self, cmd, arguments):
        for swear in self.swears:
            if swear in cmd:
                return True
            for arg in arguments:
                if swear in arg:
                    return True
        return False

    def make_guess(self, user, letter):
        if user.id not in self.score_system.users:
            self.say("Who are you? Type \"hm: join\" to join!")
            return
        if not self.hm.game_state == "started":
            self.saypush("No game in progress, type \"hm: start\" to start one!\n")
            return
        ret = self.hm.guess(letter)
        if ret == "invalid":
            self.saypush(letter + " is not a valid guess.\n")
        elif ret == "repeat":
            self.saypush("Someone already guessed " + letter + "\n")
        elif ret == "hit":
            self.saypush(utils.randomelement(self.hit))
            self.score_system.score_correct_guess(user)
            self.turn_end(user)
        elif ret == "miss":
            self.saypush(utils.randomelement(self.miss))
            self.score_system.score_incorrect_guess(user)
            self.turn_end(user)
        return

    # Perform common actions at end of turn
    def turn_end(self, user):
        self.display()
        if self.hm.game_state == "win":
            self.score_system.score_win_game(user)
            self.score_system.save_to_file()
        elif self.hm.game_state == "lose":
            self.score_system.score_lose_game(user)
            self.score_system.save_to_file()

