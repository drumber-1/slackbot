import basicbot
import markovchain as mchain

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
        if self.should_speak():
            print("Parsed messages : " + str(self.mc.parsed_messages))
            print(self.mc.generate_text())

    def should_speak(self):
        if self.mc.parsed_messages % 10 == 0:
            return True
        else:
            return False


