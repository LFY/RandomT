from realfunc import *
from funcclass import *

def advect(f, v, x, t):
	return f(x - v * t)

from RandomT import *

class AddFlip(RandomRealFunction):
	def __init__(self):
		def draw():
			x = float(randint(0, 1))
			return RealFunction(lambda y: y + x)
		RandomRealFunction.__init__(self, lambda : draw())

class UFunc(RandomRealFunction):
	def __init__(self, a, b):
		def draw():
			x = float(uniform(a, b))
			return RealFunction(lambda y: x)
		RandomRealFunction.__init__(self, lambda : draw())

RandomFunction = Random(Function)

class PerturbedSine(RandomFunction):
	def __init__(self):
		def draw():
			u = float(uniform(0, 1))
			return Function(lambda x: sin(x) + u)
		RandomFunction.__init__(self, lambda : draw())


from math import sin

U = UFunc(-0.2, 0.2)

RandomSine = U + RealFunction(lambda x: sin(x))

Advect = rnd(advect)

def forward_UQ():
	print "Uncertain initial condition: E[u] @ t = 0, 1, 5, 10:"

	print Expectation(Advect(RandomSine, 1, 0, 0))
	print Expectation(Advect(RandomSine, 1, 0, 1))
	print Expectation(Advect(RandomSine, 1, 0, 5))
	print Expectation(Advect(RandomSine, 1, 0, 10))

	print "Uncertain initial condition: Var[u] @ t = 0, 1, 5, 10:"

	print Variance(Advect(RandomSine, 1, 0, 0))
	print Variance(Advect(RandomSine, 1, 0, 1))
	print Variance(Advect(RandomSine, 1, 0, 5))
	print Variance(Advect(RandomSine, 1, 0, 10))

	print "Uncertain velocity: E[u] @ t = 0, 1, 5, 10:"

	print Expectation(Advect(RealFunction(lambda x: sin(x)), Uniform(1, 2), 0, 0))
	print Expectation(Advect(RealFunction(lambda x: sin(x)), Uniform(1, 2), 0, 1))
	print Expectation(Advect(RealFunction(lambda x: sin(x)), Uniform(1, 2), 0, 5))
	print Expectation(Advect(RealFunction(lambda x: sin(x)), Uniform(1, 2), 0, 10))

	print "Uncertain velocity: Var[u] @ t = 0, 1, 5, 10:"

	print Variance(Advect(RealFunction(lambda x: sin(x)), Uniform(1, 2), 0, 0))
	print Variance(Advect(RealFunction(lambda x: sin(x)), Uniform(1, 2), 0, 1))
	print Variance(Advect(RealFunction(lambda x: sin(x)), Uniform(1, 2), 0, 5))
	print Variance(Advect(RealFunction(lambda x: sin(x)), Uniform(1, 2), 0, 10))


def backward_UQ():
	
	V = Uniform(1, 2)
	U = Advect(Function(lambda x: sin(x)), V, 0, 1)
	
	print U.sample()
	print U.sample()
	print U.sample()
	print U.sample()
	print U.sample()
	print U.sample()
	print U.sample()
	print U.sample()
	print U.sample()
	print U.sample()
	print U.sample()
	
	print Pr({U: lambda x: x < -0.95})
	print Pr({V : lambda x: x > 1.5}, {U: lambda x: x < -0.95})
	

#backward_UQ()

def super_backward_UQ():
	V = Uniform(1, 2)
	U1 = Advect(Function(lambda x: sin(x)), V, 0, 1)
	U5 = Advect(Function(lambda x: sin(x)), V, 0, 5)
	U10 = Advect(Function(lambda x: sin(x)), V, 0, 10)

	print "%f %f %f\n" % (U1.sample(), U5.sample(), U10.sample())
	print "%f %f %f\n" % (U1.sample(), U5.sample(), U10.sample())
	print "%f %f %f\n" % (U1.sample(), U5.sample(), U10.sample())
	print "%f %f %f\n" % (U1.sample(), U5.sample(), U10.sample())
	print "%f %f %f\n" % (U1.sample(), U5.sample(), U10.sample())
	print "%f %f %f\n" % (U1.sample(), U5.sample(), U10.sample())
	print "%f %f %f\n" % (U1.sample(), U5.sample(), U10.sample())
	print "%f %f %f\n" % (U1.sample(), U5.sample(), U10.sample())
	
	print Expectation(U10)
	print Variance(U10)
	
	print advect(lambda x: sin(x), 1.7, 0, 1)
	print advect(lambda x: sin(x), 1.7, 0, 5)
	print advect(lambda x: sin(x), 1.7, 0, 10)
	
	print Pr({V: lambda x: x > 1.6 and x < 1.8}, {U1: lambda x: x < -0.5, U5: lambda x: x < -0.5, U10: lambda x: x > 0.5})

forward_UQ()

