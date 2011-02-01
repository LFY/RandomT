from monad import *
from classdict import *

# Probability representation. TODO: Should be "continuation" representations, so Sampler vs. Dist is dealt with at a lower level.
from probrep import Computation
from probrep import Sampler
from probrep import Probability

from distrep import Dist

from random import uniform

# Putting together the classdict transformation.

def rnd_unwrap(R):
	return R.sample()

def rnd(f):
	return bind(f, Random_, lambda x: x.sample())

import inspect

# Restricts to method types.
class ProbMethodRestrictor(DictOp):
	def __init__(self):
		self.op = DictTypeFilter(FunctionType, type(int.__add__), type(list.insert))

#ProbDecorate = DictValueMap(lambda f: rnd(f))

def rand_method(self, f, *args, **kwargs):
	return RandomClassMethod(f, self)(*args, **kwargs)
	
ProbDecorate = DictValueMap(lambda f: rnd(f))

MixinComputation = DictOp(dict_add, Computation.__dict__)
MixinSampler = DictOp(dict_add, Sampler.__dict__)
MixinProbRep = DictOp(dict_add, Probability.__dict__)
#RDT = DictTransform(MethodRestrictor(), MetaPropertyExcluder(), ProbDecorate, MixinProbRep, MethodRestrictor(), MetaPropertyExcluder())

RDT = DictTransform(MethodRestrictor(), MetaPropertyExcluder(), ProbDecorate, MixinComputation, MixinSampler, MixinProbRep, ProbMethodRestrictor(), MetaPropertyExcluder())

# The Random metaclass.
class Random_(type):
	def __new__(meta, classname, bases, classDict):
		# If we're already trying to transform a Random type, dont do any decoration, use Python's default class construction.
		if type(bases[0]) is Random_:
			return type.__new__(meta, classname, bases, classDict)
		else: # Else, promote the class as follows:
			
			# Dictionary transformation: bind all member functions, mix in probabilistic calculations.
			newClassDict = RDT(bases[0].__dict__)
			
			def promote(*args):
				newargs = []
				for a in args:
					if type(type(a)) is Random_:
						newargs.append(a)
					else:
						newargs.append(Probability(a))
				return newargs

			def custom_constructor(self, *args):
				self.dist = None
				self.cpt = None
				self.smp_cache = None

				self.exact = False

				self.net = None
				self.lazynet = None
				self.srcname = ""

				if len(filter(lambda x: not x.exact, args[1:])) == 0:
					self.exact = True
				
				if len(args) > 0 and isFunction(args[0]): # Should work like Sampler
					newargs = args[1:]
					self.args = promote(*newargs)
					self.src = lambda *a : args[0](*a)
					self.srcname = args[0].__name__
#					self.src = args[0]
				else: # Should work like the base class constructor
				
					# the case where we're fed a Dist as the constructing argument
					if len(args) == 1 and type(args[0]) == Dist:
						self.dist = Dist(args[0])
						self.exact = True
						self.args = []
					else:
						#if bases[0] is not list and bases[0] is not dict:
						val = bases[0](*args)
						self.dist = Dist({val : 1})
						self.exact = True
						
						self.args = promote(*args)
						self.src = lambda *a: bases[0](*a)
					self.src = self.dist.sample
# COMMON================================================================	
				self.samples = []
				
			newClassDict['__init__'] = custom_constructor
			return type.__new__(meta, classname, (), newClassDict)

# A type constructing function.
def Random(base_type):
	#return construct_class(base_type, Random_)
	#new_type = construct_with_bases(base_type, Random_)
	new_type = construct_class(base_type, Random_)
	if not hasattr(base_type, '__hash__'):
		new_type.__hash__ = lambda self: id(self)
	return new_type

from digraph import Digraph
from digraph import top_sort

def inheritance_graph(t, res = {}):
	if len(t.__bases__) == 0:
		return Digraph(res).reverse()
	else:
		res[t] = []
		for b in t.__bases__:
			res[t].append(b)
		return inheritance_graph(b, res)

# For defining types that have expected value and variance.
def VectorSpaceRandom(base_type, zero=None, addition=None, scalar_mult=None, product=None):
	new_type = Random(base_type)
	if zero is not None and addition is not None and scalar_mult is not None:
		def _expectation(x, samples=9001):
			# Assume the default value is zero.
			res = zero()
						
			# perform integration.
			if x.dist is not None:
				for (v, p) in x.dist.items():
					res = addition(res, scalar_mult(v, p))
				return res
			else:
				for i in range(samples):
					res = addition(res, x.sample())
				return scalar_mult(res, (1.0 / samples))

		new_type.expect = _expectation
	
	if product is not None and hasattr(new_type, 'expect'):
		def _variance(x, samples=9001):
			exp = x.expect(samples)
			return rnd(product)(x, x).expect(samples) - product(exp, exp)
		def _covariance(x, y, samples=9001):
			return rnd(product)(x, y).expect(samples) - product(x.expect(samples), y.expect(samples))
		new_type.var = _variance
		new_type.covar = _covariance
	
	return new_type

# Similar concept to above, but expectation and variance are defined in terms of an integration operator.
def IntegrableRandom(base_type, integrator=None, product=None):
	pass
