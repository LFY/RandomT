from decimal import *
from randomt import Random
from random import uniform
from probrep import Dist

RandomDecimal = Random(Decimal)

class Uniform(RandomDecimal):
	def __init__(self, a, b, l=0):
		if l == 0:
			RandomDecimal.__init__(self, lambda : Decimal(str(uniform(a, b))))
		else:
			def uniform_discrete(a, b, l):
				r = range(l + 1)
				a = Decimal(str(a))
				b = Decimal(str(b))
				l = Decimal(str(l))
				res = map(lambda x: x / l, r)
				res = map(lambda x: x * (b - a), res)
				res = map(lambda x: x + a, res)
				return res
			
			vals = uniform_discrete(a, b, l)
			RandomDecimal.__init__(self, Dist(zip(vals, len(vals) * [1.0 / len(vals)])))
