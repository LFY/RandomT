def normalize(xs):
	s = float(sum(xs))
	return map(lambda x: x / s, xs)

class Table(object):
	def __init__(self, colnames):
		self.colnames = colnames
		self.rowdata = []
		self.coldata = {}
		for n in self.colnames:
			self.coldata[n] = []
			
	def addRow(self, _row_dict):
		# preproject
		row_dict = dict(filter(lambda (k, v): k in self.colnames, _row_dict.items()))
		
		self.rowdata.append(dict(row_dict))
		
		for (k, v) in row_dict.items():
			self.coldata[k].append(v)

	def getElem(self, col, row):
		return self.coldata[col][row]
	
	def getRow(self, row):
		return self.rowdata[row]

	def getLastRow(self):
		return self.rowdata[-1]
		
	def getCol(self, col):
		if col not in self.coldata.keys():
			return []
		else:
			return self.coldata[col]
	
	def getDomain(self, col):
		return set(self.getCol(col))
		
	def printInfo(self,):
		for r in self.rowdata:
			print r
	
	def projectRow(self, p):
		return dict(filter(lambda (k, v): k in self.colnames, p.items()))
	
	def hasRow(self, query):
		# performs projection automatically, so this works for query rows that contain a superset of the columns of this table
		q = self.projectRow(query)
		return q in self.rowdata
	
	def rows(self,):
		return list(self.rowdata)
		
	def numRows(self,):
		return len(self.rowdata)

	def indexOf(self, row):
		assert(self.hasRow(row))
		return self.rowdata.index(self.projectRow(row))

	# returns rows where col_predicate = {col: predicate}, values of col satisfy predicate (AND)
	def selectWhere(self, _col_predicate):
		col_predicate = self.projectRow(_col_predicate)
		to_return = []
		# go through the dumb way for now
		for r in self.rowdata:
			match = True
			for (c, p) in col_predicate.items():
				if callable(p):
					match = match and p(r[c])
				else:
					match = match and r[c] == p
			if match:
				to_return.append(dict(r))
		return to_return

	def selectWhereT(self, pred):
		return makeTable(self.colnames, self.selectWhere(pred))
	
	def truncate(self, n):
		self.rowdata = self.rowdata[:n]
		for (k, v) in self.coldata.items():
			self.coldata[k] = v[:n]

def makeTable(colnames, rows):
	res = Table(colnames)
	for r in rows:
		res.addRow(r)
	return res

# doms: a dictionary of {key: [values in domain]}
# result: a table containing the cartesian product; each row is a combination.
def cartesian(doms):
	names = doms.keys()
	domains = doms.values()
	
	res = Table(names)
	
	from itertools import product
	
	for vs in product(*domains):
		row = {}
		for (n, v) in zip(names, vs):
			row[n] = v
		res.addRow(row)
	
	return res
	
# performs natural join on tables a and b
def natural_join(a, b):
	a_cols = set(a.colnames)
	b_cols = set(b.colnames)
	res_cols = a_cols.union(b_cols)

	res_doms = {}
	for c in res_cols:
		a_dom = a.getDomain(c)
		b_dom = b.getDomain(c)
		res_doms[c] = list(a_dom.union(b_dom))

	return cartesian(res_doms)
	
def table_test():
	t = Table(('X', 'Y', 'Z'))
	t.addRow({'X': 0, 'Y': 1, 'Z': 2})
	t.addRow({'X': 1, 'Y': 0, 'Z': 3})
	
	t.printInfo()
	
	print t.getCol('X')
	print t.getElem('X', 1)
	
	A = Table(('A'))
	B = Table(('B'))
	A.addRow({'A': 0})
	A.addRow({'A': 1})
	B.addRow({'B': 0})
	B.addRow({'B': 1})
	
	print "table A:"
	A.printInfo()
	
	print "table B:"
	B.printInfo()
	
	C = natural_join(A, B)
	
	print "C = A natural join B. Table C:"
	C.printInfo()
	
	print "table D:"
	D = Table(('B', 'X'))
	D.addRow({'B': 0, 'X': 0})
	D.addRow({'B': 1, 'X': 0})
	D.addRow({'B': 0, 'X': 0})
	D.printInfo()
	
	print "E = C natural join D. Table E:"
	E = natural_join(C, D)
	
	E.printInfo()
	
	print "is A=0, X=0, B=1 in E?"
	print E.hasRow({'A' : 0, 'B' : 1, 'X': 0})
	
	print "Simple selectwhere test:"
	print E.selectWhere({'A': lambda x: x > 0})
	
class FactorTable(Table):
	def __init__(self, distr, names):
		Table.__init__(self, names)
		if type(distr) is not tuple:
			self.distr = tuple((distr,))
		else:
			self.distr = distr
		self.probs = []
		self.summed = []
	
	def __eq__(self, other):
		return set(self.distr) == set(other.distr) and set(self.getargs()) == set(other.getargs())
			
	def getargs(self,):
		return self.colnames
	
	def renorm(self,):
		assert(reduce(lambda a, b: a and b, [x >= 0 for x in self.probs], True))
		if sum(self.probs) == 0.0:
			return self.probs
		self.probs = normalize(self.probs)
		
	def addObservation(self, obs_dict, prob):
		self.addRow(obs_dict)
		self.probs.append(prob)

	def printInfo(self,):
		print "Factor for %s with arguments %s, summed out %s" % (self.distr, self.colnames, self.summed)
		for (r, p) in zip(self.rowdata, self.probs):
			print "observation: %s probability: %s" % (r, p)

	def __repr__(self,):
		res = ""
		res += "Factor for %s summed out %s\n" % (self.distr, self.summed)
		res += "Arguments: %s\n" % self.rowdata[0].keys()
		for (r, p) in zip(self.rowdata, self.probs):
			res += "observation: %s probability: %s\n" % (r.values(), p)
		return res
		
	def probOf(self, obs):
		if self.hasRow(obs):
			return self.probs[self.indexOf(obs)]
		else:
			return 0.0

	def setProb(self, obs, p):
		self.probs[self.indexOf(obs)] = p
	
# another constructor function
def makeFactorTable(distr, names, obs, probs):
	res = FactorTable(distr, names)
	for (o, p) in zip(obs, probs):
		res.addObservation(o, p)
	return res

# creates a copy
def copyFactorTable(t):
	return makeFactorTable(t.distr, t.colnames, t.rows(), t.probs)

# conditions the cpt on the specified condition, which is a dictionary of {var: bool function} predicates (AND)
# returns a new factor table conditioned on the evidence
def condition(t, cond):
	newrows = t.selectWhere(cond)
	newprobs = map(lambda x: t.probOf(x), newrows)
	newtable = makeFactorTable(t.distr, t.colnames, newrows, newprobs)
	newtable.renorm()
	return newtable

def query(t, cond):
	return reduce(lambda x, y: x + y, map(lambda r: t.probOf(r), t.selectWhere(cond)),0.0)

def projectTable(t, vs):
	newnames = filter(lambda x: x in vs, t.colnames)
	newtable = Table(newnames)
	for r in t.rows():
		newtable.addRow(r)
	return newtable

def project(t, vs):
	newdistr = filter(lambda x: x in vs, t.distr)
	newnames = filter(lambda x: x in vs, t.colnames)
	newtable = FactorTable(newdistr, newnames)
	for (r, p) in zip(t.rows(), t.probs):
		newtable.addObservation(r, p)

	return newtable

def drop_impossible(t):
	row_prob = zip(t.rows(), t.probs)
	filtered_row_prob = filter(lambda (x, y): y > 0.0, row_prob)
	
	filtered_row_prob_t = zip(*filtered_row_prob)
	
	new_rows = filtered_row_prob_t[0]
	new_probs = filtered_row_prob_t[1]

	newtable = makeFactorTable(t.distr, t.colnames, new_rows, new_probs)
	newtable.renorm()
	return newtable

def logged(func):
	def call(*args, **kwargs):
		print 'calling %s' % func.__name__
		return func(*args, **kwargs)
	return call
		
# returns the pointwise product of CPT's a and b by taking the natural join
def pointwise_product(a, b):
	def is_projection(t1, t2):
		return set(t1.colnames).issubset(set(t2.colnames))
	
	a_sub_b = is_projection(a, b)
	b_sub_a = is_projection(b, a)
	
	def ptwise_project(small, big):
		res = FactorTable(tuple(big.distr), big.colnames)
		for r in big.rows():
			small_prob = small.probOf(r)
			big_prob = big.probOf(r)
			res.addObservation(r, small_prob * big_prob)
		return res
	
	if a_sub_b:
		return ptwise_project(a, b)
	elif b_sub_a:
		return ptwise_project(b, a)
	else:
		res_table = natural_join(a, b)
	
		res_ftable = FactorTable(tuple(set(a.distr).union(b.distr)), res_table.colnames)
	
		for r in res_table.rows():
			a_prob = a.probOf(r)
			b_prob = b.probOf(r)
			res_ftable.addObservation(r, a_prob * b_prob)
	
		return res_ftable

# sums out variable v from factor table t, returns new table
def sum_out(t, v):
	if v not in t.colnames:
		return copyFactorTable(t)
		
	newvars = filter(lambda x: x is not v, t.colnames)
	res_table = FactorTable(t.distr, newvars)
	res_table.summed = t.summed + [v]

	doms = {}
	for c in newvars:
		doms[c] = t.getDomain(c)
	
	T = cartesian(doms)
	
	for r in T.rows():
		sumrows = t.selectWhere(r)
		newprob = reduce(lambda x, y: x + y, map(lambda x: t.probOf(x), sumrows), 0.0)
		res_table.addObservation(r, newprob)
	
	return res_table	
	
def factor_table_test():
	T = FactorTable('X', ('X', 'Y', 'Z'))
	
	o1 = {'X' : 0, 'Y' : 0, 'Z' : 0}
	o2 = {'X' : 1, 'Y' : 0, 'Z' : 1}
	o3 = {'X' : 0, 'Y' : 1, 'Z' : 1}
	o4 = {'X' : 1, 'Y' : 1, 'Z' : 2}
	
	T.addObservation(o1, 1.0)
	T.addObservation(o2, 1.0)
	T.addObservation(o3, 1.0)
	T.addObservation(o4, 1.0)
	
	T.renorm()
	
	T.printInfo()
	
	S = makeFactorTable('X', ('X', 'Y', 'Z'), (o1, o2, o3, o4), (1.0, 1.0, 1.0, 1.0))
	S.printInfo()	
	
	print 'Pointwise product test:'
	
	X = FactorTable('X', ('X'))
	X.addObservation({'X': 0}, 0.5)
	X.addObservation({'X': 1}, 0.5)
	
	X.printInfo()
	
	Y = FactorTable('Y', ('Y'))
	Y.addObservation({'Y': 0}, 0.5)
	Y.addObservation({'Y': 1}, 0.5)
	
	Y.printInfo()
	
	Z = pointwise_product(X, Y)
	Z.printInfo()
	
	print 'summing out X'
	Z = sum_out(Z, 'X')
	Z.printInfo()
	
	print 'construct from Dist object:'
	A = Dist({0: 1.0, 1: 1.0, 2: 1.0})
	B = dist_to_factor('A', A)
	B.printInfo()

def rn_example():
	
	T = True
	F = False
	
	B = makeFactorTable('B', ('B'), ({'B': T}, {'B': F}), (.001, .999))
	E = makeFactorTable('E', ('E'), ({'E': T}, {'E': F}), (.002, .998))
	
	a1 = {'A': T, 'B': T, 'E': T}
	a2 = {'A': T, 'B': F, 'E': T}
	a3 = {'A': T, 'B': T, 'E': F}
	a4 = {'A': T, 'B': F, 'E': F}
	
	a1f = {'A': F, 'B': T, 'E': T}
	a2f = {'A': F, 'B': F, 'E': T}
	a3f = {'A': F, 'B': T, 'E': F}
	a4f = {'A': F, 'B': F, 'E': F}
	
	A = makeFactorTable('A', ('A', 'B', 'E'), (a1, a2, a3, a4, a1f, a2f, a3f, a4f), (.95, .29, .94, .001, .05, .71, .06, .999))
	#A = makeFactorTable('A', ('A', 'B', 'E'), (a1, a2, a3, a4), (.95, .29, .94, .001))
	
	j1 = {'J': T, 'A': T}
	j2 = {'J': T, 'A': F}
	
	j1f = {'J': F, 'A': T}
	j2f = {'J': F, 'A': F}

	
	J = makeFactorTable('J', ('J', 'A'), (j1, j2, j1f, j2f), (.90, .05, .10, .95))
	#J = makeFactorTable('J', ('J', 'A'), (j1, j2), (.90, .05))
	J = condition(J, {'J': lambda x: x == T})
	
	m1 = {'M': T, 'A': T}
	m2 = {'M': T, 'A': F}
	
	m1f = {'M': F, 'A': T}
	m2f = {'M': F, 'A': F}
	
	M = makeFactorTable('M', ('M', 'A'), (m1, m2, m1f, m2f), (.70, .01, .30, .99))
	#M = makeFactorTable('M', ('M', 'A'), (m1, m2), (.70, .01))
	M = condition(M, {'M': lambda x: x == T})
	
	print 'Bayes net from Russel Norvig 14.4'
	B.printInfo()
	E.printInfo()
	A.printInfo()
	J.printInfo()
	M.printInfo()
	
	print 'what is the probability of a burglary given that john and mary called?'
	print 'i.e., query variable: B, evidence: J=T, M=T. hidden: A, E'
	
	print 'Pick A to eliminate first.'
	
	print 'First need to take product of all factors A is incident to'
	
	print 'A is incident to A, J, M.'
	
	AJM = pointwise_product(A, pointwise_product(J, M))
	AJM.printInfo()
	AJM = sum_out(AJM, 'A')
	AJM.printInfo()
	
	print 'Next, want to eliminate E.'
	print 'E is incident to AJM, E.'
	
	EAJM = pointwise_product(E, AJM)
	EAJM.printInfo()
	
	EAJM = sum_out(EAJM, 'E')
	EAJM.printInfo()
	
	print 'Now, we can find the distribution of B by taking the pointwise product with B.'
	
	BEAJM = pointwise_product(B, EAJM)
	BEAJM.printInfo()
	
	print 'Renormalized, this is:'
	BEAJM.renorm()
	BEAJM.printInfo()
	
	
	print 'So about a 28% chance of burglary.'
	
	def nextStep():
		# Next step: find out how to integrate this with the Computation and Probability classes automatically.
		# Something like this:
		B = Flip(.001)
		E = Flip(.002)
		def alarmSound(b, e):
			if b and e:
				return Flip(.95)
			elif not b and e:
				return Flip(.29)
			elif b and not e:
				return Flip(.94)
			elif not b and not e:
				return Flip(.001)
		A = rnd(alarmSound)(B, E)
		# alternatively, A can just be specfied through constructing the factor table. these two things should be interchangeable. 
		J = Cond(A, Flip(.90), Flip(.05))
		M = Cond(A, Flip(.70), Flip(.01))

def copy_test():
	X = FactorTable('X', ('X'))
	X.addObservation({'X': 0}, 0.5)
	X.addObservation({'X': 1}, 0.5)
	
	X.printInfo()
	
	Y = copyFactorTable(X)
	Y.addObservation({'X': 2}, 0.5)
	Y.printInfo()
	
	X.printInfo()
	
	condition(X, {'X': lambda x: x > 0}).printInfo()

	
if __name__ == '__main__':

#	table_test()
#	factor_table_test()
	rn_example()
#	copy_test()
