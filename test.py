import basics
import hangmanbot
import os
import signal

key_test = ""  # api key goes here

def handle_pdb(sig, frame):
	import pdb
	pdb.Pdb().set_trace(frame)

def main():
	bh = basics.BotHandler(key_test)
	bh.add_bot(hangmanbot.HangmanBot("general"))
	while True:
		bh.update()

if __name__ == "__main__":
	signal.signal(signal.SIGUSR1, handle_pdb)
	print("Starting with process ID: " + str(os.getpid()))
	main()
