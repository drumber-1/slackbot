import hangmanbot
import adventurebot
import markovbot

api_key = ""  # Your slack api key here

def runHangman():
    dictionaries = []
    dictionaries.append(hangmanbot.Dictionary("./hangmanbot/words.txt", name="Basic dictionary", weighting=90))
    dictionaries.append(hangmanbot.Dictionary("./hangmanbot/enable.txt", name="Enhanced North American Benchmark Lexicon (ENABLE)", weighting=5))
    dictionaries.append(hangmanbot.Dictionary("./hangmanbot/sowpods.txt", name="Tournament scrabble dictionary (SOWPODS)", weighting=3))
    dictionaries.append(hangmanbot.Dictionary("/usr/share/dict/words", name="Unix dictionary", weighting=2))

    hm = hangmanbot.HangmanBot(api_key, "general", dictionaries)
    hm.run_forever()

def runAdventure():
    ad = adventurebot.AdventureBot(api_key, "general")
    ad.run_forever()

def runMarkov():
    mk = markovbot.MarkovBot(api_key, "general")
    mk.run_forever()

if __name__ == "__main__":

    runHangman()
    #runAdventure()
    #runMarkov()
