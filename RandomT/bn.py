from cpt import FactorTable
from cpt import Table

from digraph import Digraph

from probrep import evalVar

# 1:1 distr : vertex correspondence
def tables_to_digraph(ts):
	table_map = {}
	for t in ts:
		assert(len(t.distr) == 1)
		table_map[t.distr[0]] = t
	
	incidence_map = {}
	for (d, t) in table_map.items():
		incidence_map[d] = list(filter(lambda x: x is not d, t.getargs())) # no self-incidences
	
	return Digraph(incidence_map)

def variables_to_digraph(vs):
	incidence_map = {}
	# Anything that this depends upon that we don't have in the network? Add it.
	def all_visible_vars(vs, result=[]):
		all_args = reduce(lambda x, y: x + y, map(lambda v: list(v.args), vs))
		if len(all_args) == 0:
			return result
		else:
			return all_visible_vars(all_args, result + all_args)

	all_visibles = all_visible_vars(list(vs))
	all_vars = list(vs) + all_visibles

	for v in all_vars:
		incidence_map[v] = v.args
	
	return Digraph(incidence_map)

# lazy bayes net, instead of taking a bunch of factor tables, it takes a bunch of Computations.
# for sampling.
class LazyNet(object):
	def __init__(self, vars):
		self.min_samples = 9001

		self.graph = variables_to_digraph(vars)
		self.funcmap = {}
		for v in self.graph.verts():
			self.funcmap[v] = v.src

		self.samples = Table(self.getvars())
		
		self.assn_order = self.get_assn_order()
		self.assn_order_arg_indices = [map(lambda x: self.assn_order.index(x), v.args) for v in self.assn_order]
	
	# Should be a way to write these as structural induction instead
	def get_assn_order(self, partial={}, order=[]):
		if set(self.getvars()).issubset(set(partial.keys())):
			return order
		else:
			new_assn = dict(partial)
			def args_fulfilled(v):
				return len(self.graph.children(v)) == 0 or set(self.graph.children(v)).issubset(set(partial.keys()))

			with_arguments = filter(lambda v: args_fulfilled(v), self.getvars())
			viable = filter(lambda x: x not in partial.keys(), with_arguments)
			new_order = order + list(viable)
			
			def get_assignment(v):
				arglist = map(lambda x: partial[x], v.args)
				return evalVar(v, *arglist)

			def set_assignment(var, val):
				new_assn[var] = val

			# So very un-functional.
			map(lambda v: set_assignment(v, get_assignment(v)), viable)

			return self.get_assn_order(new_assn, new_order)
	
	def eval_var(self, partial, v):
		if len(v.args) == 0:
			return evalVar(v)
		else:
			arglist = map(lambda x: partial[x], v.args)
			return evalVar(v, *arglist)

	def construct_assignment3(self, relevant=[]):
		res = range(len(self.assn_order))
		for i in range(len(self.assn_order)):
			if len(self.assn_order[i].args) == 0:
				res[i] = evalVar(self.assn_order[i])
			else:
				arglist = map(lambda x: res[x], self.assn_order_arg_indices[i])
				res[i] = evalVar(self.assn_order[i], *arglist)
		if relevant == []:
			return dict(zip(self.assn_order, res))
		else:
			newdict = []
			for (k, v) in zip(self.assn_order, res):
				if k in relevant:
					newdict.append((k, v))
			return dict(newdict)			

	def construct_assignment2(self, partial={}):
		for o in self.assn_order:
			newval = self.eval_var(partial, o)
			partial.update({o : newval})
		
		return partial
				
	def printInfo(self):
		print self.graph
		print self.funcmap

	def getvars(self):
		return self.funcmap.keys()

	def construct_assignment(self, partial={}):
		if set(self.getvars()).issubset(set(partial.keys())):
			return partial
		else:
			new_assn = dict(partial)
			def args_fulfilled(v):
				return len(v.args) == 0 or set(v.args).issubset(set(partial.keys()))

			with_arguments = filter(lambda v: args_fulfilled(v), self.getvars())
			viable = filter(lambda x: x not in partial.keys(), with_arguments)

			def get_assignment(v):
				arglist = map(lambda x: partial[x], v.args)
				return evalVar(v, *arglist)

			def set_assignment(var, val):
				new_assn[var] = val

			map(lambda v: set_assignment(v, get_assignment(v)), viable)

			return self.construct_assignment(new_assn)

	def add_sample(self, assignment):
		self.samples.addRow(assignment)

	def fill_samples(self, target=-1):
		if target < 0:
			target = self.min_samples

		while self.samples.numRows() < target:
			self.prior_sample()
		if self.samples.numRows() > target:
			self.samples.truncate(target)		

	def clear_samples(self):
		self.samples = Table(self.getvars())

	def prior_sample(self):
		self.add_sample(self.construct_assignment3())
		return self.samples.getLastRow()
		
	def conditional_sample(self, evidence={}):
		return self.construct_assignment(evidence)
		
	def rejection_ask(self, _query, evidence={}, N=-1):
		if N < 0:
			N = self.min_samples

		from cpt import makeTable
		from cpt import projectTable

#		self.fill_samples(N)
			
		query_evidence = {}
		if type(_query) is dict:
			query_evidence.update(_query)
			query = list(_query.keys())
		elif type(_query) is list or type(_query) is tuple:
			query = list(_query)
		else:
			query = list([_query])

		relevant_vars = list(query) + list(evidence.keys())
		T = Table(relevant_vars)
		for i in range(N):
			T.addRow(self.construct_assignment3(relevant_vars))
					
		evidence_consistent = projectTable(T.selectWhereT(evidence), query)
	
		if len(query_evidence.keys()) > 0: # Returns a float
			query_consistent = evidence_consistent.selectWhereT(query_evidence)
			return float(query_consistent.numRows()) / float(evidence_consistent.numRows())
		else: # Returns a dictionary with an approximating distribution
			rowdata = evidence_consistent.rows()
			values = map(lambda x: tuple(x.values()), rowdata)
			flat_vals = map(lambda e: e[0] if len(e) is 1 else e, values)

			hist = {}
			for v in flat_vals:
				hist[v] = 0
			for v in flat_vals:
				hist[v] += 1

			# Normalization step
			for (k, v) in hist.items():
				hist[k] = v / float(len(flat_vals))

			return hist
			
		return T


	def MCMC(self, query, evidence={}, proposal=None):
		pass
		
	def getNamedDigraph(self, names={}):
		if names == {}:
			return self.graph
		else:
			new_verts = [names[v] for v in self.graph.verts()]
			new_adjs = [map(lambda x: names[x], self.graph.children(v)) for v in self.graph.verts()]
			return Digraph(dict(zip(new_verts, new_adjs))).reverse()
	
def getLN(var):
	return LazyNet((var,))

def sampleVar(var, evidence={}):
	return getLN(var).conditional_sample(evidence)[var]

class BayesNet(object):
	def __init__(self, tables):
		# remove duplicates
		
		table_map = {}
		for t in tables:
			assert(len(t.distr) == 1)
			table_map[t.distr[0]] = t
			
		self.graph = tables_to_digraph(tables)
		self.cptmap = {}
		for v in self.graph.verts():
			self.cptmap[v] = table_map[v]
		
		self.canonical_order = self.get_canonical_ordering()
	
	# find the canonical ordering, that is, going from things with 0 args to the root of the graph.
	def get_canonical_ordering(self, order = []):
		if len(order) == len(self.graph.verts()):
			return order
		else:
			def args_fulfilled(v):
				return len(self.graph.children(v)) == 0 or set(self.graph.children(v)).issubset(set(order))
			
			fulfilled_args = filter(lambda v: args_fulfilled(v), self.getvars())
			viable = filter(lambda x: x not in order, fulfilled_args)
			new_order = order + list(viable)				
			return self.get_canonical_ordering(new_order)
				
	def printInfo(self):
		print self.graph
		print self.cptmap

	def getvars(self,):
		return self.cptmap.keys()
	
	# From Russel & Norvig Fig 14.10
	# query: a single variable that is the query variable
	# evidence: dictionary of {var: val} pairs
	# Does not work correctly
	def elimination_ask(self, query, evidence={}):
		work_tables = []
		
		# New ordering.
		work_vars = self.canonical_order
		
		def hidden(v):
			return v is not query and v not in evidence.keys()
		
		from cpt import copyFactorTable
		from cpt import condition
		
		def make_factor(v, e):
			t = copyFactorTable(self.cptmap[v])
			
			if v in e.keys():
				t = condition(t, e)
			
			return t
			
		from cpt import sum_out
			
		def sumout(v, ts):
			return map(lambda x: sum_out(x, v), ts)
		
		from cpt import pointwise_product
					
		for v in work_vars:
			print 'creating factor for %s given %s' % (v, evidence)
			work_tables.append(make_factor(v, evidence))
			print 'current work tables:'
			print work_tables
			if hidden(v):
				print '%s is hidden so summing out over current work tables' % (v)
				work_tables = sumout(v, work_tables)
				print 'work tables after summing out %s' % (v)
				print work_tables
		
		print 'final product:'
		print work_tables
		res = reduce(lambda x, y: pointwise_product(x, y), work_tables)
		
		for v in filter(lambda x: x is not query, res.distr):
			res = sum_out(res, v)
		res.renorm()
		return res

	# another variable elimination algorithm based more on what ive seen in taht variable elimination applet / my intuition
	def varelim(self, _query, evidence={}):
		from cpt import sum_out
		from cpt import pointwise_product
		from cpt import copyFactorTable
		from cpt import condition
		from cpt import drop_impossible
		from digraph import shortest_path
		
		query_evidence = {}
		if type(_query) is dict:
			query_evidence.update(_query)
			query = list(_query.keys())
		elif type(_query) is list or type(_query) is tuple:
			query = list(_query)
		else:
			query = list([_query])
			
		def hidden(v):
			return v not in query			
		
		def incident_tables(v, ts):
			return filter(lambda t: v in t.getargs(), ts)
		
		def nonincident_tables(v, ts):
			return filter(lambda t: v not in t.getargs(), ts)
		
		def make_factor(v, e):
			t = copyFactorTable(self.cptmap[v])
			if not set(t.getargs()).isdisjoint(set(e.keys())):
				t = condition(t, e)
			return t
		
		def relevant(v):
			targets = evidence.keys() + query
			path = map(lambda x: shortest_path(self.graph.rep, x, v), targets)
			path = reduce(lambda x, y: x + y, path, [])
			return len(path) > 0
		
		# filter irrelevant variables. 
		work_vars = filter(lambda x: relevant(x), self.canonical_order)
		work_tables = map(lambda x: make_factor(x, evidence), work_vars)

		for v in work_vars:
			if hidden(v):
				incident = incident_tables(v, work_tables)
				product = reduce(lambda x, y: pointwise_product(x, y), incident)
				summed = sum_out(product, v)
				
				# FIXME; that's another search through the network every time
				work_tables = nonincident_tables(v, work_tables) + [summed]
		# multiply all tables.
		result = drop_impossible(reduce(lambda x, y: pointwise_product(x, y), work_tables))
		
		result.renorm()
		
		return result

	def rejection_sample(self, _query, evidence={}):
		pass


# merges the two bayes nets. graph theoretically, will append adjacencies.
def merge_bn(a, b):
	return BayesNet(a.cptmap.values() + b.cptmap.values())

def merge_ln(a, b):
	return LazyNet(a.getvars() + b.getvars())

def basic_test():
	X = FactorTable('X', ('X',))
	X.addObservation({'X': 0}, 0.5)
	X.addObservation({'X': 1}, 0.5)
	
	X.printInfo()
	
	Y = FactorTable('Y', ('Y',))
	Y.addObservation({'Y': 0}, 0.5)
	Y.addObservation({'Y': 1}, 0.5)
	
	Y.printInfo()
	
	Z = FactorTable('Z', ('X', 'Y', 'Z'))
	
	o1 = {'X' : 0, 'Y' : 0, 'Z' : 0}
	o2 = {'X' : 1, 'Y' : 0, 'Z' : 1}
	o3 = {'X' : 0, 'Y' : 1, 'Z' : 1}
	o4 = {'X' : 1, 'Y' : 1, 'Z' : 2}
	
	Z.addObservation(o1, 0.25)
	Z.addObservation(o2, 0.25)
	Z.addObservation(o3, 0.25)
	Z.addObservation(o4, 0.25)
	
	Z.printInfo()
	
	G = BayesNet((X, Y, Z))
	
	print 'Query: Pr(Z | X == 0)'
	G.elimination_ask('Z', {'X': lambda x: x == 0}).printInfo()
	
	print 'Query: Pr(Z | X == 1, Y == 1)'
	G.elimination_ask('Z', {'X': lambda x: x == 1, 'Y': lambda y: y == 1}).printInfo()
	
	print 'Query: Pr(Z)'
	G.elimination_ask('Z').printInfo()
	
	print 'Query: Pr(Z | Z == 2)'
	G.elimination_ask('Z', {'Z': lambda z: z == 2}).printInfo()
	
	pass

def varelim_test():
	X = FactorTable('X', ('X',))
	X.addObservation({'X': 0}, 0.5)
	X.addObservation({'X': 1}, 0.5)
	
	X.printInfo()
	
	Y = FactorTable('Y', ('Y',))
	Y.addObservation({'Y': 0}, 0.5)
	Y.addObservation({'Y': 1}, 0.5)
	
	Y.printInfo()
	
	X2 = FactorTable('X', ('X',))
	X.addObservation({'X': 0}, 0.5)
	X.addObservation({'X': 1}, 0.5)
	
	X3 = FactorTable('X', ('X',))
	X.addObservation({'X': 0}, 0.2)
	X.addObservation({'X': 1}, 0.8)
	
	Z = FactorTable('Z', ('X', 'Y', 'Z'))
	
	o1 = {'X' : 0, 'Y' : 0, 'Z' : 0}
	o2 = {'X' : 1, 'Y' : 0, 'Z' : 1}
	o3 = {'X' : 0, 'Y' : 1, 'Z' : 1}
	o4 = {'X' : 1, 'Y' : 1, 'Z' : 2}
	
	Z.addObservation(o1, 0.25)
	Z.addObservation(o2, 0.25)
	Z.addObservation(o3, 0.25)
	Z.addObservation(o4, 0.25)
	
	print X == X2
	print X == X3
	print Y == X
	
	N = BayesNet((X, Y, Z))
	print N.varelim('Z')

def nonuniform_test():
	X = FactorTable('X', ('X',))
	X.addObservation({'X': 0}, 0.9)
	X.addObservation({'X': 1}, 0.1)
	
	Y = FactorTable('Y', ('Y',))
	Y.addObservation({'Y': 0}, 0.1)
	Y.addObservation({'Y': 1}, 0.9)
	
	Z = FactorTable('Z', ('X', 'Y', 'Z'))
	
	o1 = {'X' : 0, 'Y' : 0, 'Z' : 0}
	o2 = {'X' : 1, 'Y' : 0, 'Z' : 1}
	o3 = {'X' : 0, 'Y' : 1, 'Z' : 1}
	o4 = {'X' : 1, 'Y' : 1, 'Z' : 2}
	
	Z.addObservation(o1, 1.0)
	Z.addObservation(o2, 1.0)
	Z.addObservation(o3, 1.0)
	Z.addObservation(o4, 1.0)
	
	N = BayesNet((X, Y, Z))
	print N.varelim('Z')

def sumout_test():
	from cpt import pointwise_product
	from cpt import sum_out
	
	X = FactorTable('X', ('X',))
	X.addObservation({'X': 0}, 0.9)
	X.addObservation({'X': 1}, 0.1)
	
	Y = FactorTable('Y', ('Y',))
	Y.addObservation({'Y': 0}, 0.1)
	Y.addObservation({'Y': 1}, 0.9)
	
	Z = FactorTable('Z', ('X', 'Y', 'Z'))
	
	o1 = {'X' : 0, 'Y' : 0, 'Z' : 0}
	o2 = {'X' : 1, 'Y' : 0, 'Z' : 1}
	o3 = {'X' : 0, 'Y' : 1, 'Z' : 1}
	o4 = {'X' : 1, 'Y' : 1, 'Z' : 2}
	
	Z.addObservation(o1, 1.0)
	Z.addObservation(o2, 1.0)
	Z.addObservation(o3, 1.0)
	Z.addObservation(o4, 1.0)
	
	ZY = pointwise_product(Z, Y)
	print ZY

def condition_test():
	from cpt import pointwise_product
	from cpt import sum_out
	from cpt import condition
	
	X = FactorTable('X', ('X',))
	X.addObservation({'X': 0}, 0.5)
	X.addObservation({'X': 1}, 0.5)
	
	Y = FactorTable('Y', ('Y',))
	Y.addObservation({'Y': 0}, 0.1)
	Y.addObservation({'Y': 1}, 0.9)
	
	Z = FactorTable('Z', ('X', 'Y', 'Z'))
	
	o1 = {'X' : 0, 'Y' : 0, 'Z' : 0}
	o2 = {'X' : 1, 'Y' : 0, 'Z' : 1}
	o3 = {'X' : 0, 'Y' : 1, 'Z' : 1}
	o4 = {'X' : 1, 'Y' : 1, 'Z' : 2}
	
	Z.addObservation(o1, 1.0)
	Z.addObservation(o2, 1.0)
	Z.addObservation(o3, 1.0)
	Z.addObservation(o4, 1.0)
	
	N = BayesNet((X, Y, Z))
	T = N.varelim('Z')
	
	from cpt import query
	
	print query(T, {'Z': 0})
	
#	ZY = pointwise_product(Z, Y)

if __name__ == '__main__':
#	basic_test()
#	varelim_test()
#	nonuniform_test()
#	sumout_test()
#	condition_test()
	merge_test()
