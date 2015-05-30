import random

def randomelement(elements):
	return elements[random.randint(0, len(elements) - 1)]

def read_responses(fname):
	responses = []
	f = open(fname)
	for line in f:
		responses.append(line)
	return responses
