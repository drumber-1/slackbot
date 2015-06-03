import slacker
import command_system
import requests

# Prints out a dictionary all nice like
# Useful for debugging
def print_dict(d):
	for k, v in sorted(d.items()):
		print(u"{0}: {1}".format(k, v))


# Other bots should be a sub class of BasicBot
#
# Messages are added to a message string via say,
# and pushed to slack via push
# This allows multiple messages to be sent in a single api request
class BasicBot(object):
	def __init__(self, botname, short_name, channel, avatar="", descripton=""):
		self.name = botname
		self.allowed_channel = channel
		self.short_name = short_name

		self.pic = avatar
		self.description = descripton

		self.handler = None
		self.message = ""
		self.command_system = command_system.CommandSystem()

		self.command_system.add_command("help", self.say_help, "Show help message")

	def set_handler(self, handler):
		self.handler = handler

	def say(self, text):
		self.message += text

	def push(self):
		if self.message[-1] == '\n':
			self.message = self.message[:-1]
		print("(bot) pushing message")
		try:
			channel_id = self.handler.channel_id(self.allowed_channel)
			self.handler.api.chat.post_message(channel_id, self.message, username=self.name, icon_url=self.pic)
		except slacker.Error as e:
			print("(bot) Error: " + str(e) + " when pushing to channel " + self.allowed_channel)
		else:
			print("(bot) pushing successful")

		self.message = ""

	def saypush(self, text):
		self.say(text)
		self.push()

	def process(self, message):
		text = message["text"].lower()
		if not text.startswith(self.short_name + ":"):
			return

		cmd = text[len(self.short_name) + 1:].strip()  # Get actual command
		splt_cmd = cmd.split()
		if len(cmd) == 0:
			self.saypush("You gotta say something dude")
			return
		command = splt_cmd[0]
		arguments = splt_cmd[1:]
		user = {"id": message["user"], "name": self.handler.users[message["user"]]}

		if not self.command_system.process(user, command, arguments):
			self.unknown_command(user, command, arguments)
		return

	def say_help(self):
		if self.description != "":
			self.say(self.description + "\n\n")
		self.say("Prefix commands with \"" + self.short_name + ":\"\n")
		self.say(self.command_system.get_help())
		self.push()

	def unknown_command(self, user, cmd, arguments):
		self.saypush("Unknown command: " + str(cmd))


class BotHandler(object):
	def __init__(self, key):
		self.api = slacker.Slacker(key)
		self.channels = {}
		self.users = {}
		self.bots = []
		self.test()
		self.create_channel_list()
		self.create_user_list()

	def add_bot(self, bot):
		self.bots.append(bot)
		bot.set_handler(self)
		self.channels[self.channel_id(bot.allowed_channel)][2] = True

	def test(self):
		r = self.api.auth.test()
		print("Connected via to team {0} via user {1}".format(r.body["team"], r.body["user"]))

	def get_users(self):
		return self.api.users.list().body['members']

	def get_channels(self):
		return self.api.channels.list().body['channels']

	def get_messages(self, channel, latest=None, oldest=None, count=None):
		return self.api.channels.history(channel, latest=latest, oldest=oldest, count=count).body['messages']

	def print_last_message(self, channel):
		print_dict(self.get_new_messages(channel, force=True)[0])

	def get_new_messages(self, channel, count=1, force=False):
		if force:
			ms = self.get_messages(channel, count=count)
		else:
			ms = self.get_messages(channel, count=count, oldest=self.channels[channel][1])
			if len(ms) > 0:
				self.channels[channel][1] = ms[0]['ts']
		return ms

	def create_channel_list(self):
		cs = self.get_channels()
		self.channels.clear()
		for c in cs:
			self.channels[c["id"]] = [c["name"], 0, False]
			self.get_new_messages(c["id"])  # Updates ts timestamp

	def create_user_list(self):
		us = self.get_users()
		self.users.clear()
		for u in us:
			self.users[u["id"]] = u["name"]

	def user_id(self, search_name):
		for user_id, name in self.users.items():
			if search_name == search_name:
				return user_id
		return None

	def channel_id(self, search_name):
		for channel_id, channel in self.channels.items():
			if channel[0] == search_name:
				return channel_id
		return None

	def update(self):
		for ck in self.channels.keys():
			if not self.channels[ck][2]:  # Channel has no bots in it, skip
				continue
			try:
				new_messages = self.get_new_messages(ck, count=10)
				new_messages.reverse()  # Want to process the oldest message first
				if len(new_messages) > 0:
					print("(handler) Got " + str(len(new_messages)) + " new messages from " + self.channels[ck][0])
			except slacker.Error as e:
				print("(handler) slacker.Error getting messages: " + str(e))
				continue
			except requests.exceptions.RequestException as e:
				print("(handler) RequestException getting messages: " + str(e))
				continue

			for b in self.bots:
				if not self.channels[ck][0] == b.allowed_channel:
					continue

				for m in new_messages:
					if "user" not in m:  # Probably a bot message or something
						continue
					if not m["user"] in self.users:  # We don't know this user
						continue
					b.process(m)
