# Slackbots

A collection of generally entertaining slackbots, written in python using slack's python-slackclient.

###Requirements
* python 3
* slack-client (https://github.com/slackhq/python-slackclient)

###Optional
* Tweepy (http://www.tweepy.org/) (Optional for MarkovBot)

###Quick start

Make a bot user for your slack team (https://api.slack.com/bot-users), then fire up your favourite python2.7 interpreter:

```
import markovbot
mk = markovbot.MarkovBot("this_is_your_api_key", "general")
mk.runforever()
```

See ```main_example.py``` for minimum working examples for each bot. The basic functionality of each bot is detailed below.

###Bots

####MarkovBot

Generates messages based on a probabilistic model of previous messages. Any time markovbot is mentioned he will respond with a randomly generated message. All other messages in the channel will be used to train the markov chain. Markovbot will ignore messages that are less than 4 words, more than 25 words or contain a mention of another user. Allow around 20-30 input messages before the output becomes interesting. I accept no responsibility for anything markovbot says.


```markovbot.MarkovBot(api_key, channel, grouping=2, logfile=None, unprompted=True, twitter_api=None)```

| Argument | Description |
|:-------- |:----------- |
| ```api_key``` | Your api key for the slack bot |
| ```channel``` | The channel the bot will post messages to, either name or id |
| ```grouping``` | How many words are considered when generating the next word. High values give better messages but require a lot more training to get original messages. 2 generally is a good value/ |
| ```logfile``` | If not ```None```, a log will be kept in ```logfile``` of what the bot is saying and who it is responding to. |
| ```unprompted``` | If ```True``` will generate messages randomly without being asked (about every 70 messages from other users) |
| ```twitter_api``` | If this is an instance of a tweepy api object (see http://docs.tweepy.org/en/v3.5.0/auth_tutorial.html) any pinned markovbot message will be tweeted for safe keeping |


####HangmanBot

Play hangman! Get points! Have fun and stuff!

```hangmanbot.HangManBot(api_key, channel, dictionaries, antibot=False, scoring="basic")```

| Argument | Description |
|:-------- |:----------- |
| ```api_key``` | Your api key for the slack bot |
| ```channel``` | The channel the bot will post messages to, either name or id |
| ```dictionaries``` | A list of the dictionaries to use, as defined below |
| ```antibot``` | If ```true``` enable measures to thwart bot players |
| ```scoring``` | Scoring system, can be either "basic", "diff", "steal", detailed below |

#####Commands

All command must be prefixed with "hm:"

| Command | Description |
|:-------- |:----------- |
| ```help``` | Show help message |
| ```join``` | Adds you to the scoreboard and allows you to play |
| ```start``` | Start a game |
| ```<single letter>``` | Guess a letter during a game |
| ```dictionaries``` | Show which dictionaries are in use |
| ```show``` | Show current game state |
| ```score``` | Show current scores |
| ```points``` | Show the current scoring system |
| ```difficulty``` | Show current difficulty ("diff" or "steal" scoring only) |
| ```stats```  | Show your stats ("diff" or "steal"  scoring only) |
| ```steal <target>``` | Steal from target  ("steal" scoring only) |

#####Scoring Systems

Scores are kept in a file named ```scores.json``` in the ```hangmanbot``` folder.

| System | Description |
|:-------- |:----------- |
| ```basic``` | Gain points for getting stuff right, lose points for getting stuff wrong. |
| ```diff``` | Dynamic difficulty. Removes some guesses when several games are won in a row. |
| ```steal``` | Winning games allows the winner to steal someone else's points. |

#####Dictionaries

Hangman bot supports multiple dictionaries, given as a list:

```
dictionaries = []
dictionaries.append(hangmanbot.Dictionary("./hangmanbot/words.txt", name="Basic dictionary", weighting=90))
dictionaries.append(hangmanbot.Dictionary("./hangmanbot/enable.txt", name="Enhanced North American Benchmark Lexicon (ENABLE)", weighting=5))
dictionaries.append(hangmanbot.Dictionary("./hangmanbot/sowpods.txt", name="Tournament scrabble dictionary (SOWPODS)", weighting=3))
dictionaries.append(hangmanbot.Dictionary("/usr/share/dict/words", name="Unix dictionary", weighting=2))
```

Words will be chosen from a random dictionary according to their weightings. Weightings will be normalised so they do not need to sum to any particular value.

####AdventureBot

Play the classic Colossal Caves adventure game, in slack! Wraps the python port of colossal caves adventure by brandon rhodes (https://github.com/brandon-rhodes/python-adventure)

```adventurebot.AdventureBot(api_key, channel)```

| Argument | Description |
|:-------- |:----------- |
| ```api_key``` | Your api key for the slack bot |
| ```channel``` | The channel the bot will post message to, either name or id |

#####Commands

All command must be prefixed with "ad:"

| Command | Description |
|:-------- |:----------- |
| ```restart``` | Restart game |
| ```save <savename>``` | Save state to <savename> |
| ```load <savename>``` | Load state from <savename> |
| ```saves``` | List saves |
| ```<Anything else>``` | Send commands to cave adventure (GO NORTH, OPEN GATE, etc) |
