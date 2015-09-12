import basicbot
import command_system
import sys

class CommandBot(basicbot.BasicBot):
	def __init__(self, api_key, channel, short_name, description=""):
		super(CommandBot, self).__init__(api_key, channel)
		self.short_name = short_name
		self.description = description

		self.command_system = command_system.CommandSystem()
		self.command_system.add_command("help", self.say_help, "Show help message")

	def process_event(self, event):
		if "type" in event:  # Errors / message confirmation don't have type
			if event["type"] == "message":
				self.process_message(event)
			else:
				self.runoff_event(event)

	def process_message(self, message):
		if "subtype" in message:
			if message["subtype"] == "message_changed":
				self.process_message(message["message"])
				return

		if "user" in message:
			if message["user"] not in self.users:
				print("(commandbot) {user} not recognised)".format(user=message["user"]["name"]))
				return
			user = self.users[message["user"]]

			text = message["text"].lower()
			if not text.startswith(self.short_name + ":"):
				return
		else:
			print("(commandbot) No user field in message, probably a bot or something")
			return

		cmd = text[len(self.short_name) + 1:].strip()  # Get actual command
		splt_cmd = cmd.split()
		if len(cmd) == 0:
			self.saypush("You gotta say something dude")
			return
		command = splt_cmd[0]
		arguments = splt_cmd[1:]

		sys.stdout.write("(commandbot) Got command: \"" + command + "\"")
		if len(arguments) != 0:
			sys.stdout.write(" with arguments: " + str(arguments))
		sys.stdout.write("\n")
		if not self.command_system.process(user, command, arguments):
			if not self.runoff_message(user, command, arguments, message):
				print("(commandbot) Command unrecognised")
				self.unknown_command(user, command, arguments)
		return

	def say_help(self):
		if self.description != "":
			self.say(self.description + "\n\n")
		self.say("Prefix commands with \"" + self.short_name + ":\"\n")
		self.say(self.command_system.get_help())
		self.push()

	def runoff_event(self, event):
		return False

	def runoff_message(self, user, cmd, arguments, message):
		return False

	def unknown_command(self, user, cmd, arguments):
		self.saypush("Unknown command: " + str(cmd))
