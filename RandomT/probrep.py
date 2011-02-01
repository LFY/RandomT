from random import uniform
from bn import BayesNet
from bn import LazyNet
from cpt import FactorTable
from itertools import product
from functional import isFunction

from distrep import Dist
	
def dist_to_factor(name, dist):
	res = FactorTable(name, (name,))
	for (v, p) in dist.items():
		res.addObservation({name: v}, p)
	return res

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
# COMMON==================================================================

	def __eq__(self, other):
		return self.__hash__() == other.__hash__()
	def __hash__(self,):
		return self.__repr__().__hash__()
	
	def getLN(self,):
		return LazyNet((self,))
		if self.lazynet is None:
			self.lazynet = LazyNet((self,))
		return self.lazynet
	
	def eval(self, *args):
		return self.src(*args)
		
		
	def info(self,):
		return "Random<T>: self=%s src=%s args=%s\n" % (self, self.src, self.args) 
	
	def full_info(self, l=1):
		if len(self.args) == 0:
			return self.info()
		else:
			return self.info() + "\n" + reduce(lambda x, y: x + y, [l * "\t" + a.full_info(l + 1) for a in self.args])

	def get_src(self,):
		return self.src

	def get_args(self,):
		return self.args
	
# Would be nice to remove this too.
class Sampler(Computation):
	def get_sample(self,):
		self.sample_leaves()
		self.sample_trunk()
		val = self.smp_cache
		return val
	
	def invalidate_cache(self,):
		args = self.get_args()
		if len(args) == 0:
			self.smp_cache = None
		else:
			self.smp_cache = None
			for a in args:
				a.invalidate_cache()
	
	# Contains flattening; move this somewhere else or don't do it at all
	def sample_trunk(self,):
		func = self.get_src()
		args = self.get_args()

		if len(args) == 0:
			return self.smp_cache
		else:
			self.smp_cache = func(*map(lambda x: x.sample_trunk(), args))
			
			return self.smp_cache

	# also contains flattening
	def sample_leaves(self,):
		func = self.get_src()
		args = self.get_args()
		
		if len(args) == 0:
			self.smp_cache = func()
		else:
			for a in args:
				a.sample_leaves()
	
	def sample_fixed(self,):
		return self.sample_trunk()
		
	def info(self,):
		return "Random<T>: self=%s src=%s args=%s smp=%s dist=%s\n" % (self, self.get_src(), self.get_args(), self.smp_cache, self.dist) 
	
class Probability(Sampler):
	# Now: Sample conditioned on evidence, by retrieving the lazynet and producing samples from there.
	def sample(self, evidence={}):
		if evidence == {}:
			return self.get_sample()
		else:
			return self.getLN().conditional_sample(evidence)[self]			
	
	def debug_sample(self,):
		return self.debug_get_sample()
