import markovbot

api_key = ""  # Your slack api key here

def runMarkov():
    mk = markovbot.MarkovBot(api_key, "general")
    mk.run_forever()

if __name__ == "__main__":

    runHangman()
