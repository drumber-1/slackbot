import os
import random
import re
import pprint

import basicbot
import markovchain as mchain


class MarkovBot(basicbot.BasicBot):
    def __init__(self, api_key, channel, grouping=2, logfile=None, unprompted=True):
        super(MarkovBot, self).__init__(api_key, channel)

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

    def process_event(self, event):
        if "type" in event:  # Errors / message confirmation don't have type
            if event["type"] == "message":
                self.process_message(event)

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
