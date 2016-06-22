import os

import basicbot
import adventure
import utils

class AdventureBot(basicbot.BasicBot):
    def __init__(self, api_key, channel):
        super(AdventureBot, self).__init__(api_key, channel)

        self.short_name = "ad"
        self.savefile = "main.adv"

        self.game = None

        if not os.path.isfile(self.savefile):
            self.game = adventure.game.Game()
            adventure.load_advent_dat(self.game)
            self.game.start()
            self.saypush(utils.correct_case(self.game.output))
            self.saypush("(Use \"ad: <command>\")")
        else:
            self.game = adventure.game.Game.resume(self.savefile)
            self.saypush(utils.correct_case(self.game.do_command(["look"])))

    def process_event(self, event):
        if "type" in event:  # Errors / message confirmation don't have type
            if event["type"] == "message":
                self.process_message(event)

    def process_message(self, message):
        if "subtype" in message:
            if message["subtype"] == "message_changed":
                self.process_message(message["message"])
                return

        text = message["text"].lower()
        if not text.startswith(self.short_name + ":"):
            return

        cmd = text[len(self.short_name) + 1:].strip()  # Get actual command
        splt_cmd = cmd.split()

        if (splt_cmd[0] == "restart"):
            self.game = adventure.game.Game()
            adventure.load_advent_dat(self.game)
            self.game.start()
            self.saypush(utils.correct_case(self.game.output))
            self.saypush("(Use \"ad: <command>\")")
        elif (splt_cmd[0] == "save"):
            if len(splt_cmd) >= 2:
                filename = str(splt_cmd[1]) + ".adv"
                self.game.output = ""
                self.game.t_suspend("save", filename)
                self.saypush(utils.correct_case(self.game.output))
            else:
                self.game.output = ""
                self.game.t_suspend("save", self.savefile)
                self.saypush(utils.correct_case(self.game.output))
        elif (splt_cmd[0] == "load"):
            if len(splt_cmd) >= 2:
                filename = str(splt_cmd[1]) + ".adv"
                if not os.path.isfile(filename):
                    self.saypush("No file with that name!")
                else:
                    self.game = adventure.game.Game.resume(filename)
                    self.saypush(utils.correct_case(self.game.do_command(["look"])))
            else:
                self.game = adventure.game.Game.resume(self.savefile)
                self.saypush(utils.correct_case(self.game.do_command(["look"])))
        elif (splt_cmd[0] == "saves"):
            self.say("Save files:\n")
            for f in os.listdir("."):
                if f.endswith(".adv"):
                    self.say("\t" + f + "\n")
            self.push()
        else:
            self.saypush(utils.correct_case(self.game.do_command(splt_cmd)))
