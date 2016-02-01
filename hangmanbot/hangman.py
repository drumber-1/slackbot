import random
import re

class Hangman(object):
    def __init__(self, dictionaries):
        self.dictionaries = dictionaries
        self.dictionary_total_weighting = 0
        for d in self.dictionaries:
            self.dictionary_total_weighting += d.weighting
    
        self.game_state = "ready"
        self.word = ""
        self.blank_char = "-"
        self.letters_missed = ""
        self.letters_guessed = ""
        self.started = False
        self.difficulty = 0
        self.difficulty_current = 0  # Increasing the difficulty will only take place for the next game
        self.re_include = re.compile("^[a-z]+$")
        
        self.state_prefix = "+---+\n"
        self.state_suffix = "|         \n" + "==========\n"

        self.states = ["|   |     \n" +
                       "|         \n" + 
                       "|         \n" +
                       "|         \n",
                       "|   |     \n" +
                       "|   0     \n" +
                       "|         \n" +
                       "|         \n",
                       "|   |     \n" +
                       "|   0     \n" +
                       "|   |     \n" +
                       "|         \n",
                       "|   |     \n" +
                       "|   0     \n" +
                       "|  /|     \n" +
                       "|         \n",
                       "|   |     \n" +
                       "|   0     \n" +
                       "|  /|\    \n" +
                       "|         \n",
                       "|   |     \n" +
                       "|   0     \n" +
                       "|  /|\    \n" +
                       "|  /      \n",
                       "|   |     \n" +
                       "|   0     \n" +
                       "|  /|\    \n" +
                       "|  / \    \n"]
                       

    def start(self):
        dictionary = self.random_dictionary()
        self.word = dictionary.get_random_word()
        print("(hangmanbot) " + self.word)
        self.letters_missed = ""
        self.letters_guessed = ""
        self.started = True
        self.difficulty_current = self.difficulty
        self.game_state = "started"
        return dictionary

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
            print("(hangmanbot) Cannot set difficulty to " + str(new_difficulty) + " (min 0)")
            return
        if new_difficulty > (len(self.states) - 1):
            print("(hangmanbot) Cannot set difficulty to " + str(new_difficulty) + " (max " + str(
                len(self.states) - 1) + ")")
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
            
    def random_dictionary(self):
        if len(self.dictionaries) == 1:
            return self.dictionaries[0]
            
        x = random.randint(1, self.dictionary_total_weighting)
        
        running_weighting = 0
        for d in self.dictionaries:
            running_weighting += d.weighting
            if x <= running_weighting:
                return d
        
        print("(hangmanbot) An error has occured choosing a dictionary!")
        raise Exception

