import os
import random
import re
import pprint

import markovbot.markovchain as mchain
import markovbot.reactiondata


class MarkovBot():
    def __init__(self,
                mc_savefile="data/chain.dat",
                reaction_savefile="data/reactions.dat",
                grouping=2,
                unprompted=True,
                reactions=False,
                reaction_frequency_scale=1,
                twitter_api=None,
                twitter_delay=900,
                tweet_triggers=["heart", "+1"]):
        # twitter data
        self.twitter_api = twitter_api
        self.twitter_delay = twitter_delay
        self.tweet_triggers = tweet_triggers
        self.recent_messages = {}

        # Unprompted replies data
        self.messages_since_speak = 0
        self.unprompted = unprompted

        # main chain data
        self.mc = mchain.MarkovChain(word_grouping=grouping)
        self.mc_savefile = mc_savefile
        if os.path.isfile(self.mc_savefile):
            self.mc.load(self.mc_savefile)

        # reactions data
        if reactions:
            self.reaction_data = markovbot.reactiondata.ReactionData(reaction_frequency_scale)
        else:
            self.reaction_data = None

        self.reaction_savefile = reaction_savefile
        if self.reaction_data is not None and os.path.isfile(self.reaction_savefile):
            self.reaction_data.load(self.reaction_savefile)

    def on_message(self, text):
        response = {"message" : None, "reaction" : None}

        # Check if we want to react to the new message
        if self.reaction_data is not None:
            reaction = self.reaction_data.on_message()
            if reaction is not None:
                response["reaction"] = reaction
            self.reaction_data.save(self.reaction_savefile)

        # ignore long messages (potential spam)
        if len(text.split()) > 25:
            return response

        # add message to brain
        if self.mc.add_message(text):
            self.mc.save(self.mc_savefile)

        self.messages_since_speak += 1

        if self.should_speak():
            response["message"] = self.speak()

        return response

    def on_mention(self):
        response = {"message" : None, "reaction" : None}
        response["message"] = self.speak()

        return response

    def on_reaction(self, reaction, ts, message, message_ts, reactOnSelf):
        response = {"message" : None, "reaction" : None}
        if self.reaction_data is not None:
            self.reaction_data.on_reaction(reaction)
        
        if reactOnSelf and reaction in self.tweet_triggers:
            time_delay = ts - message_ts
            if time_delay < self.twitter_delay:
                self.send_tweet(message)

        return response

    def speak(self):
        text = self.mc.generate_text()
        self.messages_since_speak = 0
        return text

    def should_speak(self):
        if self.unprompted and self.messages_since_speak > 20 and random.randint(0, 50) == 0:
            return True
        else:
            return False

    def send_tweet(self, text):
        if self.twitter_api is not None:
            import tweepy
            try:
                self.twitter_api.update_status(text)
                print("(MarkovBot) Tweeted \"{}\"".format(str(text.encode('utf-8'))))
            except tweepy.error.TweepError as e:  # tweepy raises an exception if status is duplicate
                print("(MarkovBot) Could not tweet \"{}\"".format(str(text.encode('utf-8'))))
                print("(MarkovBot) Error message: \"{}\", code: {}".format(str(e.message[0]['message'].encode('utf-8')), e.message[0]['code']))
        else:
            print("(MarkovBot) Would of liked to tweet \"{}\"".format(str(text.encode('utf-8'))))