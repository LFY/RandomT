from randomt import Random, rnd
from random import shuffle

# Just grab the immutable methods
RandomList = Random(tuple)

class Permutation(RandomList):
	def __init__(self, _seq):
		seq = list(_seq)
		self.seq = seq[:]

		def rand():
			shuffle(self.seq)
			return tuple(self.seq)
						
		RandomList.__init__(self, rand)

Nil = RandomList(tuple())

def lst(*xs):
	return xs 
List = rnd(lst)

def cons(x, xs):
	return (x,)  + xs
Cons = rnd(cons)

def length(l):
	return len(l)
Length = rnd(length)

class MakeList(RandomList):
	def __init__(self, countModel, objectModel):
		def draw():
			return map(lambda x: objectModel(x).sample(), range(countModel.sample()))
		RandomList.__init__(self, draw)
