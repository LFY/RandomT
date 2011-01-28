from randomt import Random
from randomt import rnd

from random import uniform, choice
from probrep import Dist

RandomInt = Random(int)

from randomfloat import _expect_
from randomfloat import _var_

# From a formal math perspective, E[X] meaningless for ints, but for practical purposes, people still use it

RandomInt.expect = _expect_
RandomInt.var = _var_


class Flip(RandomInt):
    def __init__(self, p = 0.5):			
	RandomInt.__init__(self, Dist({1 : p, 0: 1.0 - p}))

class UniformInt(RandomInt):
    def __init__(self, choices):
	RandomInt.__init__(self, Dist(zip(choices, len(choices) * [1.0 / len(choices)])))

class Choice(RandomInt):
	def __init__(self, p, a, b):
		RandomInt.__init__(self, Dist({a : p, b: 1 - p}))

class Dice(UniformInt):
	def __init__(self,):
		UniformInt.__init__(self, [1,2,3,4,5,6])
		
RandomBool = Random(bool)
class Bool(RandomBool):
	def __init__(self, p = 0.5):
		RandomBool.__init__(self, Dist({True: p, False: 1.0 - p}))

@rnd
def If(x, y, z):
	return y if x else z
@rnd
def And(x, y):
	return x and y

@rnd
def Or(x, y):
	return x or y
@rnd
def Not(x):
	return not x
