from random import uniform
from bn import BayesNet
from bn import LazyNet
from cpt import FactorTable
from itertools import product
from monad import isFunction
from monad import full_unwrap

from distrep import Dist
	
def dist_to_factor(name, dist):
	res = FactorTable(name, (name,))
	for (v, p) in dist.items():
		res.addObservation({name: v}, p)
	return res

def init_one_cpt(self):
	self.domain = None
	# make the cpt

	if self.dist is not None and type(self.dist) == Dist:
		self.cpt = dist_to_factor(self, self.dist)
		self.domain = self.dist.keys()
	elif not self.exact and len(self.args) is not 0 and reduce(lambda x, y: x and y, map(lambda x: x.exact, self.args)):
		self.cpt = FactorTable(self, [self] + self.args)
		domains = map(lambda x: x.domain, self.args)
		var_dom_map = dict(zip(self.args, domains))
		# is the assigment consistent with naming.
		def is_consistent(obs):
			from digraph import edges_to_adjs
			obs_d = edges_to_adjs(obs)
			for v in obs_d.values():
				if len(set(v)) > 1:
					return False
			return True
		for x in product(*domains):
			r = self.src(*x)
			if hasattr(r, 'dist') and r.dist is not None:
				for (v, p) in r.dist.items():
					obs = zip([self] + self.args, [v] + list(x))
					if is_consistent(obs):
						self.cpt.addObservation(dict(obs), p)
			else:
				obs = zip([self] + self.args, [r] + list(x))
				if is_consistent(obs):
					self.cpt.addObservation(dict(zip([self] + self.args, [r] + list(x))), 1.0)
		self.domain = self.cpt.getDomain(self)
		self.exact = True
	if self.dist is not None and len(self.args) == 0 and type(self.dist) == Dist:
		def generating_function():
			t = uniform(0,1)
			probs = [v for (k, v) in self.dist.items()]
			vals = [k for (k, v) in self.dist.items()]
			ind = 0
							
			for i in range(len(probs)):
				if i is not 0:
					probs[i] = probs[i] + probs[i - 1]
			for i in range(len(probs)):
				if t < probs[i]:
					ind = i
					break				
			return vals[ind]

		self.src = generating_function

class Computation(object):
	def __init__(self, source, *a):
		self.dist = None
		self.cpt = None
		self.smp_cache = None

		self.exact = False

		self.net = None
		self.lazynet = None
		self.srcname = ""
		
		
		if not isFunction(source):
			if type(source) == Dist: # Dist
				self.dist = Dist(source)
				self.exact = True
			else: # constant expression
				if type(source) is not list and type(source) is not dict:
					self.dist = Dist({source : 1.0})				
					self.exact = True
				
			self.src = lambda : source
		else:
			self.src = source
			self.srcname = source.__name__
			
		self.args = a
		
# COMMON==================================================================
		self.samples = []
		self.init_cpt()

	def __eq__(self, other):
		return self.__hash__() == other.__hash__()
	def __hash__(self,):
		return self.__repr__().__hash__()
	
	def getLN(self,):
		if self.lazynet is None:
			self.lazynet = LazyNet((self,))
		return self.lazynet
	
	def eval(self, *args):
		return self.src(*args)
	
	def init_cpt(self,):
		init_one_cpt(self)

		
	# returns a bayes net
	def construct_bn(self,):
		if self.cpt == 'Placeholder CPT':
			return self.cpt
		else:
			return self.cpt
		
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
		
class Sampler(Computation):
	def get_sample(self,):
		# pop_samples -> run scheme currently only works when the composing functions are deterministic. Not a general memoization scheme.
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
				
	def sample_trunk(self,):
		func = self.get_src()
		args = self.get_args()

		if len(args) == 0:
			return self.smp_cache
		else:
			self.smp_cache = func(*map(lambda x: x.sample_trunk(), args))
			if type(type(self.smp_cache)) is not type(type(1)):
				self.smp_cache = full_unwrap(self.smp_cache, lambda x: x.get_sample())
			
			return self.smp_cache
	
	def sample_leaves(self,):
		func = self.get_src()
		args = self.get_args()
		
		if len(args) == 0:
			self.smp_cache = func()
			if type(type(self.smp_cache)) is not type(type(1)):
				self.smp_cache = full_unwrap(self.smp_cache, lambda x: x.get_sample())
		else:
			for a in args:
				a.sample_leaves()
	
	def sample_fixed(self,):
		return self.sample_trunk()
		
	   #func = self.get_src()
	   #args = self.get_args()
	   #
	   #for a in args:
	   #	assert(a.smp_cache is not None)
	   #
	   #self.smp_cache = func(*map(lambda x: x.smp_cache, args))
	   #return self.smp_cache
		
	def info(self,):
		return "Random<T>: self=%s src=%s args=%s smp=%s dist=%s\n" % (self, self.get_src(), self.get_args(), self.smp_cache, self.dist) 
	
	def fill_samples(self, N=9001):
		while len(self.samples) < N:
			self.samples.append(self.get_sample())
				
	def debug_get_sample(self,):
		print "Before Sampling"
		self.invalidate_cache()
		print self.full_info()
		
		print "Sample Leaves"
		self.sample_leaves()
		print self.full_info()
		
		print "Sample Trunk"
		self.sample_trunk()
		print self.full_info()
		
		print "Sample Fixed"
		val2 = self.sample_fixed()
		print self.full_info()
		val2 = self.sample_fixed()
		print self.full_info()
		val2 = self.sample_fixed()
		print self.full_info()
		
		val = self.smp_cache
		return val		

class Probability(Sampler):
	
	# Now: Sample conditioned on evidence, by retrieving the lazynet and producing samples from there.
	def sample(self, evidence={}):
		if evidence == {}:
			return self.get_sample()
		else:
			return self.getLN().conditional_sample(evidence)[self]			
	
	def debug_sample(self,):
		return self.debug_get_sample()
	
	def Pr_exact(self, pred, evidence={}):
		N = self.get_nets()
		return query(N.varelim(self, evidence), pred)
		
	def Pr(self, ind_func):
		samples = 9001
		positive = 0
		negative = 0
		for s in range(samples):
			if ind_func(self.sample()) is True:
				positive = positive + 1
			else:
				negative = negative + 1
		return positive / float(positive + negative)

	def Pr_eq(self, value):
		return self.Pr(lambda x: x == value)

	# Conditional probability.
	def Pr_cond(self, ind_func, cond_var):
		samples = 9001
		int_isvalue = 0
		int_notvalue = 0
		cond_isvalue = 0
		cond_notvalue = 0
		for s in range(samples):
			condval = cond_var.sample()
			if condval is True:
				cond_isvalue = cond_isvalue + 1
			else:
				cond_notvalue = cond_notvalue + 1
			selfval = self.sample()
			
			if ind_func(selfval) is True:
				if cond_var.sample_fixed() is True:
					int_isvalue = int_isvalue + 1
				else:
					int_notvalue = int_notvalue + 1
			else:
				int_notvalue = int_notvalue + 1
				
		
		Pr_intersection = int_isvalue / float(int_isvalue + int_notvalue)
		Pr_cond = cond_isvalue / float(cond_isvalue + cond_notvalue)
				
		return Pr_intersection / Pr_cond
	
	def get_nets(self):
		if self.net is None:
			def _get_nets(v):
				if len(v.args) == 0:
					return [v.cpt]
				else:
					return [v.cpt] + reduce(lambda x, y: x + y, [_get_nets(a) for a in v.args])

			# remove dupes
		
			raw = _get_nets(self)
			res = []
			for r in raw:
				if r not in res:
					res.append(r)
		
			self.net = BayesNet(res)
		
		return self.net
	
	# returns the posterior distribution.
	def get_distr(self):
		if self.dist is not None:
			return self.dist
		elif self.exact:
			N = self.get_nets()
			D = N.varelim(self)
			return oneargfactor_to_dist(D)
		else:	
			pass
			
			samples = 9001
			vals = {}
			for s in range(samples):
				v = self.sample()
			
				if vals.get(v) is None:
					vals[v] = 0.0
				else:
					vals[v] = vals[v] + 1.0 / samples
				
			return vals
			


