import markovchain
import argparse
import pprint

def pprint_dict(d):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(d)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Examine markov chain save files")
	parser.add_argument('filename', type=str, help='Markov chain file')
	parser.add_argument('-g', '--grouping', type=int, default=2, help='Word grouping in markov chain file')
	args = parser.parse_args()
	
	mc = markovchain.MarkovChain(word_grouping=args.grouping)
	mc.load(args.filename)
	mc.print_freq()
	
	pprint_dict(mc.chain)
