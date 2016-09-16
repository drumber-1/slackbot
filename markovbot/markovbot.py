import os
import random
import re
import pprint

import basicbot
import markovchain as mchain


class MarkovBot(basicbot.BasicBot):
    def __init__(self, api_key, channel, grouping=2, logfile=None, unprompted=True, twitter_api=None, twitter_delay=900, tweet_triggers=["heart", "+1"]):
        super(MarkovBot, self).__init__(api_key, channel)

        self.twitter_api = twitter_api
        self.twitter_delay = twitter_delay
        self.tweet_triggers = tweet_triggers
        self.recent_messages = {}

        self.savefile = "markovbot/chain.dat"
        if logfile is not None:
            self.message_log = open(logfile, "w")
        else:
            self.message_log = None

        self.messages_since_speak = 0
        self.unprompted = unprompted

        self.mc = mchain.MarkovChain(word_grouping=grouping)

        self.re_mention = re.compile("<[@!].+>")

        if os.path.isfile(self.savefile):
            self.mc.load(self.savefile)

    def add_recent_message(self, new_message):
        self.recent_messages = {ts: self.recent_messages[ts] for ts in self.recent_messages if float(new_message["ts"]) - float(ts) < self.twitter_delay}
        self.recent_messages[new_message["ts"]] = new_message["text"]

    def process_event(self, event):
        if "type" in event:  # Errors / message confirmation don't have type
            if event["type"] == "message":
                self.process_message(event)
            elif event["type"] == "reaction_added":
                self.process_reaction(event)
        elif "text" in event and "reply_to" in event and "ts" in event:  # message confirmation
            self.add_recent_message(event)

    def process_reaction(self, reaction):
        if reaction["reaction"] not in self.tweet_triggers:
            return
        message_ts = reaction["item"]["ts"]
        if message_ts in self.recent_messages:
            time_delay = float(reaction["event_ts"]) - float(message_ts)
            if time_delay < self.twitter_delay:
                message_text = self.recent_messages[message_ts]
                self.send_tweet(message_text)
                self.recent_messages.pop(message_ts)

    def process_message(self, message):
        if "subtype" in message:
            return
        if message["channel"] != self.channel_id:  # Skip private messages and groups
            print("(markovbot) Got non-target channel message from " + self.get_users()[message["user"]].name + ":")
            print("\t" + message["text"])
            return
        if "reply_to" in message:
            if message["reply_to"] is None:
                return
            else:
                print("Reply to not None, is: " + message["reply_to"])
        if message["user"] == "USLACKBOT":  # Ignore slackbot
            return

        if len(message["text"].split()) > 25:
            return

        if self.id in message["text"]:
            self.speak(message)
            return

        m = self.re_mention.search(message["text"])
        if m is not None:
            print ("(markovbot) message, \"" + message["text"].encode("utf-8") + "\",contains mention ignoring")
            return

        if self.mc.add_message(message["text"]):
            self.mc.save(self.savefile)

        self.messages_since_speak += 1

        if self.should_speak():
            self.speak(message)

    def speak(self, message):
        text = self.mc.generate_text()
        self.saypush(text)

        if self.message_log is not None:
            self.message_log.write("Responding to:\n")
            pprint.pprint(message, self.message_log)
            self.message_log.write("With:\n")
            self.message_log.write(text.encode("utf-8"))
            self.message_log.write("\n\n********************\n")
            self.message_log.flush()

        self.messages_since_speak = 0

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
                print("(MarkovBot) Tweeted \"{}\"".format(text.encode('utf-8')))
            except tweepy.error.TweepError:  # tweepy raises an exception if status is duplicate
                print("(MarkovBot) Could not tweet \"{}\", probably duplicate".format(text.encode('utf-8')))
        else:
            print("(MarkovBot) Would of liked to tweet \"{}\"".format(text.encode('utf-8')))

