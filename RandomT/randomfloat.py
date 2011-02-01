from randomt import Random
from randomt import rnd

from random import uniform
from probrep import Dist
from inferenceops import independent

from bn import LazyNet

RandomFloat = Random(float)

# ECF - Expectation commuting functions
ECF = {}

def addECF(name, condition=lambda *a:True):
	ECF[name] = condition

addECF('__add__')
addECF('__sub__')
addECF('__rmul__')
addECF('__getitem__')
addECF('__mul__', lambda *a: independent(*a))

# Simple pushing down of expectation.
def Expectation(v):
	name = v.srcname
	if name in ECF.keys():
		if ECF[name](*v.args):
			return v.eval(*map(lambda x: Expectation(x), v.args))
		else:
			return v.expect()
	else:
		return v.expect()
def Variance(v):
	if hasattr(v, 'var'):
		return v.var()
	else:
		return Expectation(v * v) - Expectation(v) ** 2

from functional import isFunction

# A covariance function.
def Covariance(u, v):
	return Expectation(u * v) - Expectation(u) * Expectation(v)
	
def _expect_(self, samples=9001):
	if self.dist is not None:
		res = 0.0
		for (k, v) in self.dist.items():
			res += k * v
		return res
	else:
		factor = 1.0 / samples
		res = 0.0
		for i in range(samples):
			res += self.sample() * factor
		return res

def _var_(self, samples=9001):
	if self.dist is not None:
		res = 0.0
		u = self.expect()
		for (v, p) in self.dist.items():
			res += p * (v - u)**2
		return res
	else:
		u = self.expect(samples)
		sq = rnd(pow)(self, 2)
		return sq.expect(samples) - pow(u, 2)
	
RandomFloat.expect = _expect_
RandomFloat.var = _var_

class Uniform(RandomFloat):
	def __init__(self, a, b):
		self.exp = (a + b) * 0.5
		self.variance = (a + b) ** 2 / 12.0
		RandomFloat.__init__(self, lambda : uniform(a, b))
	def expect(self):
		return self.exp
	def var(self):
		return self.variance

class UniformDiscrete(RandomFloat):
	def __init__(self, vals):
		RandomFloat.__init__(self, Dist(zip(vals, len(vals) * [1.0 / len(vals)])))

from math import log
from math import cos
from math import pi
from random import gauss

class Gaussian(RandomFloat):
	def __init__(self, mean, var):
		self.mean = mean
		self.variance = var
		RandomFloat.__init__(self, lambda : gauss(mean, var))
	def __add__(self, other):
		if type(other) is type(self):
			return Gaussian(self.mean + other.mean, self.variance + other.variance)
		else:
			return RandomFloat.__add__(self, other)


	def __sub__(self, other):
		if type(other) is type(self):
			return Gaussian(self.mean - other.mean, self.variance + other.variance)
		else:
			return RandomFloat.__sub__(self, other)
	
	def expect(self):
		return self.mean
	def var(self):
		return self.variance


import decimal
def binned(x, prec=0.1):
	return decimal.Decimal(str(x)).quantize(decimal.Decimal(str(prec)))

Binned = rnd(binned)
