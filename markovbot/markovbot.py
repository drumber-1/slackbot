import basicbot
import markovchain as mchain
import os

class MarkovBot(basicbot.BasicBot):
    def __init__(self, api_key, channel):
        super(MarkovBot, self).__init__(api_key, channel)
        
        self.savefile_2 = "markovbot/chain_2.dat"
        self.savefile_3 = "markovbot/chain_3.dat"
        
        self.mc_2 = mchain.MarkovChain(word_grouping=2)
        self.mc_3 = mchain.MarkovChain(word_grouping=3)
        
        if os.path.isfile(self.savefile_2):
        	self.mc_2.load(self.savefile_2)
        	
        if os.path.isfile(self.savefile_3):
        	self.mc_3.load(self.savefile_3)

    def process_event(self, event):
        if "type" in event:  # Errors / message confirmation don't have type
            if event["type"] == "message":
                self.process_message(event)

    def process_message(self, message):
        if "subtype" in message:
            return
        if "reply_to" in message:
            if message["reply_to"] is None:
                    return
            else:
                print("Reply to not None, is: " + message["reply_to"])

        if self.mc_2.add_message(message["text"]):
        	self.mc_2.save(self.savefile_2)
        	
        if self.mc_3.add_message(message["text"]):
        	self.mc_3.save(self.savefile_3)
        	
        if self.should_speak():
            print("Parsed messages : " + str(self.mc_2.parsed_messages))
            print("2 word grouping: " + self.mc_2.generate_text().encode('utf-8'))
            print("3 word grouping: " + self.mc_3.generate_text().encode('utf-8'))
            

    def should_speak(self):
        if self.mc_2.parsed_messages % 10 == 0:
            return True
        else:
            return False


