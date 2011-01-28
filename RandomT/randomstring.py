from randomt import Random
from random import uniform
from probrep import Dist

RandomString = Random(str)

class Coin(RandomString):
	def __init__(self):
		def flip():
			t = uniform(0, 1)
			return 'heads' if t < 0.5 else 'tails'
		RandomString.__init__(self, flip)

class UniformString(RandomString):
	def __init__(self, choices):
		RandomString.__init__(self, Dist(zip(choices, len(choices) * [1.0 / len(choices)])))