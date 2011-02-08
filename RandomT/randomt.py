from functional import *
from classdict import *

from bn import sampleVar
from probrep import Computation

from distrep import Dist

from random import uniform

# Putting together the classdict transformation.

def rnd_unwrap(R):
	return R.sample()

def rnd(f):
	return fmap(f, Random_, sampleVar)

def rfmap(f):
	return fmap(f, Random_, sampleVar)

def rbind(f):
	return bind(f, Random_, sampleVar)

import inspect

# Restricts to method types.
class ProbMethodRestrictor(DictOp):
	def __init__(self):
		self.op = DictTypeFilter(FunctionType, type(int.__add__), type(list.insert))

def rand_method(self, f, *args, **kwargs):
	return RandomClassMethod(f, self)(*args, **kwargs)
	
ProbDecorate = DictValueMap(lambda f: rfmap(f))

MixinComputation = DictOp(dict_add, Computation.__dict__)
RDT = DictTransform(MethodRestrictor(), MetaPropertyExcluder(), ProbDecorate, MixinComputation, ProbMethodRestrictor(), MetaPropertyExcluder())

# The Random metaclass.
class Random_(type):
	def __new__(meta, classname, bases, classDict):
		# We sort of need this conditional here so that subclasses of Random_ work correctly.
		if type(bases[0]) is Random_:
			#print 'is already Random_, not promoting'
			return type.__new__(meta, classname, bases, classDict)
		else: # Else, promote the class as follows:
			#print 'going to create constructor for type %s' % bases[0]
			#print bases
			#print classname
			
			newClassDict = RDT(bases[0].__dict__)
			
			def promote(*args):
				newargs = []
				for a in args:
					if type(type(a)) is Random_:
						newargs.append(a)
					else:
						newargs.append(Computation(a)) # ugly delegation to 'leaf' type. wish there was a way to take this out
				return newargs

			def custom_constructor(self, *args):
				#print args
				self.dist = None
				self.cpt = None
				self.smp_cache = None

				self.srcname = ""
				
				if len(args) > 0 and isFunction(args[0]): # Should work like Sampler
					newargs = args[1:]
					self.args = promote(*newargs)
					self.src = lambda *a : args[0](*a)
					self.srcname = args[0].__name__
				else: # Should work like the base class constructor
					if len(args) == 1 and type(args[0]) == Dist:
						self.dist = Dist(args[0])
						self.args = []
					else:
						val = bases[0](*args)
						self.dist = Dist({val : 1})
						
						self.args = promote(*args)
						self.src = lambda *a: bases[0](*a)
					self.src = self.dist.sample
	# COMMON================================================================	
				
			newClassDict['__init__'] = custom_constructor
			#print 'just made a new class'
			#print bases[0]
			#print classname
			return type.__new__(meta, classname, (), newClassDict)

# A type constructing function.
def Random(base_type):
	#return construct_class(base_type, Random_)
	#new_type = construct_with_bases(base_type, Random_)
	new_type = construct_class(base_type, Random_)
	if not hasattr(base_type, '__hash__'):
		new_type.__hash__ = lambda self: id(self)
	return new_type

# A function that does both the type construction and value construction
def RndVar(base_val):
	if type(base_val) == Dist:
		return Random(type(base_val.keys()[0]))(base_val)
	elif isFunction(base_val):
		return Random(type(base_val()))(base_val)
	else:
		return Random(type(base_val))(base_val)

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
