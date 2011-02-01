from bn import LazyNet
from inferenceops import *

class InferenceEngine(object):
	# Input: a LazyNet
	def __init__(self, expr):
		self.expr = expr
	def marginalize(self, var, evidence={}):
		pass

class RejectionSampler(InferenceEngine):
	def __init__(self, expr, samples=9001):
		InferenceEngine.__init__(self, expr)
		self.samples = samples
	def marginalize(self, var, evidence={}):
		return self.expr.rejection_ask(var, evidence, self.samples)

import cpt
from bn import BayesNet

class VarElim(InferenceEngine):
	def __init__(self, expr):
		def get_cpts(ln):
			return [x.cpt for x in ln.getvars()]
		InferenceEngine.__init__(self, expr)
		cpts = get_cpts(expr)
		self.bn = BayesNet(generate_cpts(expr)[0].values())
	def marginalize(self, var, evidence={}):
		reduced_cpt = self.bn.varelim(var, evidence)
		return to_distr(cpt.project(reduced_cpt, (var,)))


from functional import isFunction	

def Marginalize(var, evidence={}, engine_constructor=RejectionSampler):
	engine = engine_constructor(LazyNet([var] + list(evidence.keys())))
	return engine.marginalize(var, evidence)
	
def ProbOf(var_query, evidence={}, engine_constructor=RejectionSampler):
	marg_result = Marginalize(var_query.keys()[0], evidence, engine_constructor)

	query = var_query.values()[0]
	
	if isFunction(query):
		return reduce(lambda x, y: x + y, map(lambda x: marg_result[x], filter(lambda x: query(x), marg_result.keys())), 0.0)
	else:
		return reduce(lambda x, y: x + y, map(lambda x: marg_result[x], filter(lambda x: x is query, marg_result.keys())), 0.0)

def Mode(var, evidence={}, engine_constructor=RejectionSampler):
	marg_result = Marginalize(var_query.keys()[0], evidence, engine_constructor)
	return distr_to_mode(marg_result)

def Pr(_query, evidence={}, impl=None, num_samples=9001):
	query_evidence = {}
	query = None
	if type(_query) is dict:
		query_evidence.update(_query)
		query = list(_query.keys())[0]
	else:
		query = _query
	all_vars = [query]
	all_vars += evidence.keys()	

	# Delegate a possible inference algorithm if the user doesn't specify one.
	
	if impl is None:
		impl = delegate_inference(all_vars)

	if len(query_evidence.keys()) > 0:
		return ProbOf(query_evidence, evidence, impl)
	else:
		return Marginalize(query, evidence, impl)

# TODO: Make this do all the exactness detection
def delegate_inference(all_vars):
	return RejectionSampler

def ML_distr(d):
	ml_key, ml_prob = d.items()[0]
	for (k, v) in d.items():
		if v > ml_prob:
			ml_key, ml_prob = k, v
	return ml_key

def ML(query, evidence={}, alg=None):
	dist = Pr(query, evidence)
	return ML_distr(dist)
