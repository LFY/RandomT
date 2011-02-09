from random import uniform
from cpt import FactorTable
from itertools import product
from functional import isFunction

from distrep import Dist

def fromBind(v):
	return v.srcname.endswith('.bind')

# This is full flattening.
def evalVar(var, *args):
	return evalVar(var.src(*args)) if fromBind(var) else var.src(*args)

# This is delayed flattening.
def evalVar_delay(var, *args):
	return var.src(*args)

def info(var,):
	return "Random<T>: self=%s src=%s args=%s\n" % (var, var.src, var.args) 

def full_info(var, l=1):
	if len(var.args) == 0:
		return info(var)
	else:
		return info(var) + "\n" + reduce(lambda x, y: x + y, [l * "\t" + full_info(a, l + 1) for a in var.args])

# Should this instead build up the directed graph inductively?
# Computation :: self, args -> repr self, repr args
class Computation(object):
	def __init__(self, source, *a):
		self.dist = None
		self.cpt = None
		self.smp_cache = None

		self.srcname = ""
		
		self.args = a

		if not isFunction(source):
			if type(source) == Dist: # Dist
				self.dist = Dist(source)
			else: # constant expression
				if type(source) is not list and type(source) is not dict:
					self.dist = Dist({source : 1.0})				
				
			self.src = lambda : source
		else:
			self.src = source
			self.srcname = source.__name__

	def __eq__(self, other):
		return self.__hash__() == other.__hash__()
	def __hash__(self,):
		return self.__repr__().__hash__()
		

