def bnt_init():
	s = ""
#	s += 'cd ~/store/bnt\n'
#	s += 'addpath(genpathKPM(pwd))\n'
	return s

# sorted_names means sorted in topological order.
def init_bn_verts(sorted_names):
	s = ""
	s += "N = %d\n" % len(sorted_names)
	
	for i in range(len(sorted_names)):
		s += "%s = %d\n" % (sorted_names[i], i + 1) # MATLAB is one-indexed
	
	return s

def init_node_sizes(sorted_name_size):
	s = ""
	s += "node_sizes = 2 * ones(1, N);\n"
	for i in range(len(sorted_name_size)):
		s += "node_sizes(%d) = %d\n" % (i + 1, sorted_name_size[i]) # MATLAB is one-indexed
	s += "dag = zeros(N, N);\n"
	return s	

def def_dir_edge(a, b):
	s = ""
	s += "dag(%s, %s) = 1;\n" % (a, b)
	return s


# for now, we assume all nodes discrete
def init_bn_shell():
	s = ""
	s += "discrete_nodes = 1 : N\n"	
	s += "bnet = mk_bnet(dag, node_sizes, \'discrete\', discrete_nodes)\n"
	s += "bnet\n"
	return s

	
def init_one_cpt(name, sorted_row_probs):
	s = ""
	s += "if isempty(bnet.parents{%s})\n" % name
	s += "CPT = zeros(node_sizes(%s), 1);\n" % name
	s += "else\n"
	s += "CPT = zeros([node_sizes(bnet.parents{%s}) node_sizes(%s)]);\n" % (name, name)
	s += "end\n"
	
	for (r, p) in sorted_row_probs:
		s += "CPT("
		for d in r[:len(r) - 1]:
			s += str(d + 1) + "," # MATLAB is one-indexed
		s += str(r[-1] + 1) # MATLAB is one-indexed
		s += ") = %f;\n" % p
		
	s += "bnet.CPD{%s} = tabular_CPD(bnet, %s, \'CPT\', CPT);\n" % (name, name)
	
	return s


def init_inference_engine(engine_type='jtree_inf_engine'):
	s = ""
	s += "engine = %s(bnet);\n" % engine_type
	s += "evidence = cell(1, N);\n"
	return s
	
def marginalize(name):
	s = ""
	s += "[engine, loglik] = enter_evidence(engine, evidence);\n"
	s += "marg = marginal_nodes(engine, %s);\n" % name
	s += "marg.T;\n"
	return s

def output_marginalize():
	s = ""
	s += "fid = fopen('marg.mat', 'w')\n"
	s += "fprintf(fid, '%f\\n', marg.T)\n"
	s += "fclose(fid)\n"
	return s
	
def observe_evidence(name, val):
	s = ""
	s += "evidence{%s} = %d\n" % (name, val + 1) # MATLAB is one-indexed
	return s

def mpe(name):
	s = ""
	s += "mperes = find_mpe(engine, evidence);\n"
	s += "mympe = mperes{%s} - 1;\n" % name # MATLAB is one-indexed
	return s

def output_mpe():
	s = ""
	s += "fid = fopen('mpe.mat', 'w')\n"
	s += "fprintf(fid, '%f\\n', mympe)\n"
	s += "fclose(fid)\n"
	return s
	
def basic_test():
	names = ['C', 'S', 'R', 'W']
	sizes = [2, 2, 2, 2]

	from sys import stdout

	stdout.write(bnt_init())

	stdout.write(init_bn_verts(names))
	stdout.write(init_node_sizes(sizes))

	stdout.write(def_dir_edge('C', 'S'))
	stdout.write(def_dir_edge('C', 'R'))
	stdout.write(def_dir_edge('S', 'W'))
	stdout.write(def_dir_edge('R', 'W'))

	stdout.write(init_bn_shell())

	c_cpt = []
	c_cpt.append(((0,), 0.5))
	c_cpt.append(((1,), 0.5))

	stdout.write(init_one_cpt('C', c_cpt))

	r_cpt = []
	r_cpt.append(((0,0), 0.8))
	r_cpt.append(((1,0), 0.2))
	r_cpt.append(((0,1), 0.2))
	r_cpt.append(((1,1), 0.8))

	stdout.write(init_one_cpt('R', r_cpt))

	s_cpt = []
	s_cpt.append(((0,0), 0.5))
	s_cpt.append(((1,0), 0.9))
	s_cpt.append(((0,1), 0.5))
	s_cpt.append(((1,1), 0.1))

	stdout.write(init_one_cpt('S', s_cpt))

	w_cpt = []
	w_cpt.append(((0, 0, 0), 1.0))
	w_cpt.append(((1, 0, 0), 0.1))
	w_cpt.append(((0, 1, 0), 0.1))
	w_cpt.append(((1, 1, 0), 0.01))
	w_cpt.append(((0, 0, 1), 0.0))
	w_cpt.append(((1, 0, 1), 0.9))
	w_cpt.append(((0, 1, 1), 0.9))
	w_cpt.append(((1, 1, 1), 0.99))

	stdout.write(init_one_cpt('W', w_cpt))

	stdout.write(init_inference_engine())
	stdout.write(marginalize('W'))

from bn import LazyNet
from inferenceops import generate_cpts

def bnt_ordered_cpt_rows(t, top_order):
	new_rows = []
	for (r, p) in zip(t.rows(), t.probs):		
		new_row = []
		new_args = []
		for v in top_order:
			if v in r.keys():
				new_args.append(r[v])
		new_row.append(tuple(new_args))
		new_row.append(p)
		new_rows.append(new_row)
	return new_rows


from cpt import FactorTable

def bnt_redomain_table(t, ordered_domain):
	def transform_row(r):
		return dict(map(lambda (x, y): (x, ordered_domain[x][y]), r.items()))

	new_table = FactorTable(t.distr, t.colnames)
	for (r, p) in zip(t.rows(), t.probs):
		new_table.addObservation(transform_row(r), p)
	return new_table


from digraph import adjs_to_edges

def lazynet_to_bnt_spec(ln):
	var_cpt_map, top_order, ordered_domains, var_ids = generate_cpts(ln)

	s = ""

	s += bnt_init()

	top_order_ids = map(lambda x: var_ids[x], top_order)
	sizes = map(lambda x: len(ordered_domains[x]), top_order)

	s += init_bn_verts(top_order_ids)
	s += init_node_sizes(sizes)


	raw_edges = adjs_to_edges(ln.graph.rep)

	for e in raw_edges:
		if e[0] in top_order and e[1] in top_order:
			s += def_dir_edge(var_ids[e[1]], var_ids[e[0]])

	s += init_bn_shell()

	for (v, t) in var_cpt_map.items():
		s += init_one_cpt(var_ids[v], bnt_ordered_cpt_rows(bnt_redomain_table(t, ordered_domains), top_order))

	return (s, ordered_domains, var_ids)

def bnt_marginalize(var):
	pass

def finalize_script():
	return "quit\n"

def t_lazynet_to_bnt_spec():
	from randomt import rnd
	from randomt import Random
	from randomint import Flip

	@rnd
	def Grass(x, y):
		if x == 1 and y == 1:
			return Flip(0.99)
		elif x == 0 and y == 1:
			return Flip(0.9)
		elif x == 1 and y == 0:
			return Flip(0.9)
		elif x == 0 and y == 0:
			return Flip(0.0)

	@rnd
	def Sprinkler(x):
		if x == 1:
			return Flip(0.5)
		elif x == 0:
			return Flip(0.1)

	@rnd
	def Rain(x):
		if x == 1:
			return Flip(0.2)
		elif x == 0:
			return Flip(0.8)

	@rnd
	def SlipandFall(x):
		if x == 1:
			return Flip(0.7)
		elif x == 0:
			return Flip(0.2)

	@rnd
	def BrokenNeck(x):
		if x == 1:
			return Flip(0.2)
		if x == 0:
			return Flip(0.0)


	C = Flip(0.5)

	S = Sprinkler(C)

	R = Rain(C)

	W = Grass(S, R)

	#print lazynet_to_bnt_spec(LazyNet((W,)))

	X = Flip()
	Y = Flip()
	Z = Flip()
	N = X * Y + Y* Z + Z * X

#	print lazynet_to_bnt_spec(LazyNet((N,)))[0]






