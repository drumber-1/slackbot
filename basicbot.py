import time
import pprint

import slackclient
import websocket
import socket
import urllib2

class BotError(Exception):
    pass


class BasicBot(object):
    def __init__(self, api_key, channel):
        self.sc = slackclient.SlackClient(api_key)
        if self.sc.rtm_connect():
            print(
                "(bot) connected to {team} as {name}".format(team=self.sc.server.domain, name=self.sc.server.username))
        else:
            raise BotError("Could not connect to the real time message API")

        self.channel = channel
        self.users = self.get_users()
        self.channel_users = self.get_channel_users()
        self.id = self.sc.server.login_data["self"]["id"]
        self.channel_id = self.get_channel_id()
        
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
            message_abv += " ... [" + str(nlines - 1) + " additional lines]"
        print("(bot) pushing message: " + message_abv.encode('utf-8'))
        try:
        	self.sc.rtm_send_message(self.channel, self.message)
        except AttributeError:
        	import pdb; pdb.set_trace() # To catch potential bug after reconnect

        self.message = ""

    def saypush(self, text):
        self.say(text)
        self.push()

    def run_forever(self):
        while True:
            self.update()
            time.sleep(1)

    def update(self):
        events = []    
        try:
            events = self.sc.rtm_read()
        except websocket.WebSocketException as ex:
            print("(bot) websocket err: ")
            print(ex)
            self.attempt_reconnect()
        except socket.error as ex:
            print("(bot) socket err: ")
            print(ex)
            self.attempt_reconnect()
            
        for e in events:
            self.process_event(e)
            
    def attempt_reconnect(self):
        print("(bot) attempting to reconnect...")
        try:
            if self.sc.rtm_connect(reconnect=True):
                print("(bot) connected to {team} as {name}".format(team=self.sc.server.domain, name=self.sc.server.username))
            else:
                print("(bot) reconnection failed")
        except urllib2.URLError, e:
            print("(bot) URLError: {}".format(e.args))

    def get_users(self):
        users = self.sc.server.users
        users_dict = {}
        for u in users:  # There is probably a more pythonic way of doing this
            users_dict[u.id] = u
        return users_dict
    
    def get_channels(self):
        channels = self.sc.server.channels
        channel_dict = {}
        for c in channels:  # There is probably a more pythonic way of doing this
            channel_dict[c.id] = c
        return channel_dict

    def get_channel_users(self):
        channel_users = self.sc.server.channels.find(self.channel).members
        users = self.sc.server.users
        users_dict = {}
        for u in users:
            if u.id in channel_users:
                users_dict[u.id] = u
        return users_dict
    
    def get_channel_id(self):
    	channels = self.sc.server.channels
    	for c in channels:
    		if c.name == self.channel:
    			return c.id
    	raise BotError("Could not find channel " + self.channel)

    def process_event(self, event):
        pass
