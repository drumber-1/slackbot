import basicbot
import markovbot.markovchain as mchain

class MarkovBot(basicbot.BasicBot):
    def __init__(self, api_key, channel):
        super(MarkovBot, self).__init__(api_key, channel)

        self.mc = mchain.MarkovChain()

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

        self.mc.add_message(message["text"])
        self.saypush(self.mc.generate_text())


