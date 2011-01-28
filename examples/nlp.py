from RandomT import *

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
		return zip(first, second) + [(spaced[-2], spaced[-1])]
	elif model == 'unigram':
		return first + [spaced[-2], spaced[-1]]

def data_from_corpus(filename):
	f = open(filename)
	s = f.read()
	f.close()
	
	tri = parse_corpus(s, 'trigram')
	di = parse_corpus(s, 'digram')
	uni = parse_corpus(s, 'unigram')
	
	return (tri, di, uni)

from sys import argv
from sys import stdout

def exact_generate(trigram_model, digram_model, unigram_model):
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
	l = 0
	
	F = trigram_model[0]
	S = trigram_model[1]
	T = trigram_model[2]
	
	yield get_res_string()
	
	while True:
		stdout.write("generating word %d " % l)
		l = l + 1
		next_word = ""
#		posterior = Pr(trigram_model, {trigram_model[1]: res[-1], trigram_model[0]: res[-2]})
		posterior = Pr(trigram_model, {S: res[-1], F: res[-2]})
		if len(posterior.items()) > 0:
			next_word = RandomTuple(Dist(posterior))[2].sample()
			stdout.write("from trigram\n")
			res.append(next_word)
		else:
			posterior = Pr(digram_model, {digram_model[0]: res[-1]})
			if len(posterior.items()) > 0:
				next_word = RandomTuple(Dist(posterior))[1].sample()
				stdout.write("from digram\n")
				res.append(next_word)
			else:
				stdout.write("from unigram\n")
				posterior = Pr(unigram_model)
				next_word = RandomString(Dist(posterior)).sample()
				res.append(next_word)
		yield next_word
	
def generate_text(tri, di, uni, samples):
	res = []
	
	first = tri.sample()
	res.append(first[0])
	res.append(first[1])
	res.append(first[2])
	
	stdout.write('first trigram:' + str(first) + '\n')

	def next_word(word2, word1, samples_per = 9001):
		dist = Pr(tri[2], {tri[1]: word2, tri[0]: word1}, 'sample', samples_per)
		if dist == {}:
			dist = Pr(di[1], {di[0] : word2}, 'sample', samples_per)
		else:
			stdout.write("from trigram: ")
			return RandomString(Dist(dist)).sample()
		if dist == {}:
			stdout.write("from unigram: ")
			return uni.sample()
		else:
			stdout.write("from digram: ")
			return RandomString(Dist(dist)).sample()

	l = 0
	while True:
		stdout.write("generating word %d " % l)
		l = l + 1
		next = next_word(res[-1], res[-2], samples)
		res.append(next)
		
		stdout.write(next + '\n')
		stdout.flush()
		
		yield next

if __name__ == '__main__':
	argc = len(argv)
	
	filename = "arcade_culture.txt"
	
	samples = 9001
	
	length = 0
	
	if argc >= 2:
		filename = argv[1]
	if argc >= 3:
		length = int(argv[2])
	if argc >= 4:
		samples = int(argv[3])
	
	data = data_from_corpus(filename)
	
	T = learn_variable(data[0])
	D = learn_variable(data[1])
	U = learn_variable(data[2])
	
	stdout.write("Vocabulary size: %d\n" % len(U.dist.keys()))
	
	text = exact_generate(T, D, U)
	
	res = ""
	
	stdout.write("Target length: %d MC samples: %d \n" % (length, samples))
	
	if length == 0:
		while True:
			res += text.next() + " "
			stdout.write(res + '\n')
	else:
		for i in range(length):
			res += text.next() + " "
			stdout.write(res + '\n')
	
	exit(0)