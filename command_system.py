
class CommandSystem(object):
	def __init__(self):
		self.commands = {}
		self.sub_command_system = None  # For chaining command systems together

	def add_command(self, name, function, description, requires_user=False, has_args=False):
		self.commands[name] = {"function": function, "description": description, "requires_user": requires_user, "has_args": has_args}

	def process(self, user, command, arguments):
		if command not in self.commands:
			if self.sub_command_system is not None:
				return self.sub_command_system.process(user, command, arguments)
			else:
				return False
		else:
			if self.commands[command]["requires_user"]:
				if self.commands[command]["has_args"]:
					self.commands[command]["function"](user, arguments)
				else:
					self.commands[command]["function"](user)
			else:
				if self.commands[command]["has_args"]:
					self.commands[command]["function"](arguments)
				else:
					self.commands[command]["function"]()
			return True

	def get_help(self):
		help_msg = ""
		for cmd in self.commands.keys():
			help_msg += "\"" + cmd + "\" - " + self.commands[cmd]["description"] + "\n"
		if self.sub_command_system is not None:
			help_msg += self.sub_command_system.get_help()
		return help_msg
