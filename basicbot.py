import slackclient
import time
import pprint

class BotError(Exception):
	pass

class BasicBot(object):
	def __init__(self, api_key, channel):
		self.sc = slackclient.SlackClient(api_key)
		if self.sc.rtm_connect():
			print("(bot) connected to {team} as {name}".format(team=self.sc.server.domain, name=self.sc.server.username))
		else:
			raise BotError("Could not connect to the real time message API")

		self.channel = channel
		self.users = self.get_users()
		self.message = ""
		self.pp = pprint.PrettyPrinter(indent=4)

	def say(self, text):
		self.message += text

	def push(self):
		if self.message[-1] == '\n':
			self.message = self.message[:-1]
		message_abv = self.message.split("\n")[0]
		nlines = len(self.message.split("\n"))
		if nlines > 1:
			message_abv += "... [" + str(nlines - 1) + " additional lines]"
		print("(bot) pushing message: " + message_abv)
		self.sc.rtm_send_message(self.channel, self.message)

		self.message = ""

	def saypush(self, text):
		self.say(text)
		self.push()

	def run_forever(self):
		while True:
			self.update()
			time.sleep(1)

	def update(self):
		events = self.sc.rtm_read()
		for e in events:
			if "type" in e:  # Errors / message confirmation don't have type
				if e["type"] == "message":
					self.process_event(e)
			else:
				pass  # TODO: check 'ok' flag of message confirmations

	def get_users(self):
		users = self.sc.server.users
		users_dict = {}
		for u in users:  # There is probably a more pythonic way of doing this
			users_dict[u.id] = u
		return users_dict

	def process_event(self, event):
		pass
