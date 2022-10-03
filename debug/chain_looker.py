import markovchain
import argparse
import pprint
import re

def pprint_dict(d):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(d)
    
def tuple_has_poison(xs, regex="<[@!].+>"):
	for x in xs:
		if has_poison(x, regex=regex):
			return True
	return False

def has_poison(x, regex="<[@!].+>"):
	re_poison = re.compile(regex)
	m = re_poison.search(x.encode("unicode-escape"))
	return (m is not None)
	
def bad_key(chain, x):
	if x == "END":
		return False
	tuple_x = (x,)
	return (tuple_x not in chain)
	
def bad_key_tuple(chain, x):
	if "END" in x:
		return False
	return (x not in chain)
    
def filter_poison(chain, regex="<[@!].+>"):	
	re_poison = re.compile(regex)
	for ks in chain.keys():
		for k in ks: # A key is a tuple of some number of string
			if has_poison(k, regex):
				print(ks)
				chain.pop(ks, None)

	for ks in chain.keys():
		if ks == "START":
			chain[ks] = [vs for vs in chain[ks] if not tuple_has_poison(vs, regex=regex)]
		else:
			chain[ks] = [v for v in chain[ks] if not has_poison(v, regex=regex)]
			
def filter_empties(chain):
	print("Filtering empties")
	for ks in chain.keys():
		if len(chain[ks]) == 0:
			chain.pop(ks, None)
			print(ks)
			
def filter_bad_keys(chain):
	print("Filtering bad keys")
	for ks in chain.keys():
		if ks == "START":
			chain[ks] = [v for v in chain[ks] if not bad_key_tuple(chain, v)]
		else:
			chain[ks] = [v for v in chain[ks] if not bad_key(chain, v)]
	
def print_bad_keys(chain):
	for ks in chain.keys():
		if ks == "START":
			pass
		else:
			for v in chain[ks]:
				if v == "END":
					continue
				tuple_v = (v,)
				if tuple_v not in chain:
					print(v)
					
def clean(chain):
	filter_bad_keys(mc.chain)
	print("*********************")
	filter_empties(mc.chain)
	print("*********************")
	filter_bad_keys(mc.chain)
	print("*********************")
	filter_empties(mc.chain)
	print("*********************")
	print_bad_keys(mc.chain)
	print("*********************")
	filter_empties(mc.chain)
	print("*********************")
					

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Examine markov chain save files")
	parser.add_argument('filename', type=str, help='Markov chain file')
	parser.add_argument('-g', '--grouping', type=int, default=2, help='Word grouping in markov chain file')
	args = parser.parse_args()
	
	mc = markovchain.MarkovChain(word_grouping=args.grouping)
	mc.load(args.filename)
	
	import pdb; pdb.set_trace()

	#pprint_dict(mc.chain)
	#mc.print_freq()
	#filter_poison(mc.chain, regex="\\u[a-z0-9]{4}")
	#filter_poison(mc.chain, regex="^James\.$")
	#clean(mc.chain)
	
	#mc.save(args.filename)
	
	#mc.print_freq()
	#pprint_dict(mc.chain)

	
