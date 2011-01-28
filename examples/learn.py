# Rudimentary learning examples

from RandomT import *

def simple_learn():
	L = [(0, 0), (1, 1)] # Training set

	X = learn_variable(L) # Is a RandomTuple

	print Pr(X)

	print Pr({X[0] : 0}, {X[1]: 1}) # Should be zero.

# Something like a trigram language model.
def parse_corpus(s, model='trigram'):
	spaced = s.split()
	first = []
	second = []
	third = []
	for i in range(len(spaced) - 2):
		first.append(spaced[i])
		second.append(spaced[i+ 1])
		third.append(spaced[i + 2])
	if model == 'trigram':
		return zip(first, second, third)
	elif model == 'digram':
		return zip(first, second)
	elif model == 'unigram':
		return first

def string_from_file(filename):
	s = open(filename).read()
	return s

XT = learn_variable(parse_corpus(string_from_file("arcade_culture.txt"), 'trigram'))
XD = learn_variable(parse_corpus(string_from_file("arcade_culture.txt"), 'digram'))
XU = learn_variable(parse_corpus(string_from_file("arcade_culture.txt"), 'unigram'))
V = learn_variable(XU.dist.keys())

def generate_word_sequence(trigram_model, digram_model, unigram_model, length):
	res = []
	first = trigram_model.sample()
	
	res.append(first[0])
	res.append(first[1])
	res.append(first[2])
	
	def get_res_string():
		s = ""
		for r in res:
			s += r + " "
		return s
	
	for l in range(length):
		print "generating word %d of %d" % (l, length)
		next_word = ""
		posterior = Pr(trigram_model, {trigram_model[1]: res[-1], trigram_model[0] : res[-2]})
		if len(posterior.items()) > 0:
			next_word = RandomTuple(Dist(posterior))[2].sample()
			print "from trigram"
			res.append(next_word)
		else:
			posterior = Pr(digram_model, {digram_model[0]: res[-1]})
			if len(posterior.items()) > 0:
				next_word = RandomTuple(Dist(posterior))[1].sample()
				print "from digram"
				res.append(next_word)
			else:
				print "from unigram"
				posterior = Pr(unigram_model)
				next_word = RandomString(Dist(posterior)).sample()
				res.append(next_word)
		print get_res_string()
	
	res_string = ""
	for i in res:
		res_string = res_string + i + " "
	return res_string

def generate_word_sequence2(tri, di, uni, vocab, length):
	res = []
	first = tri.sample()
	
	res.append(first[0])
	res.append(first[1])
	res.append(first[2])
	
	print first
	
	
	def next_word(word2, word1, samples_per = 9001):
		res = {}
		dist = Pr(tri[2], {tri[1]: word2, tri[0]: word1}, 'sample', samples_per)
		if dist == {}:
			dist = Pr(di[1], {di[0] : word2}, 'sample', samples_per)
		else:
			print "from trigram"
			return RandomString(Dist(dist)).sample()
		if dist == {}:
			print "from unigram"
			return uni.sample()
		else:
			print "from digram"
			return RandomString(Dist(dist)).sample()
	
	for l in range(length):
		print "generating word %d of %d" % (l, length)

		next = next_word(res[-1], res[-2])
		print next
		res.append(next)

	res_string = ""
	for i in res:
		res_string = res_string + i + " "
	return res_string
	
print generate_word_sequence(XT, XD, XU, 100)
#print generate_word_sequence2(XT, XD, XU, V, 100)


		
	