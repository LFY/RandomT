from cpt import FactorTable
from probrep import Probability

from distrep import Density
from distrep import Dist

from probrep import dist_to_factor
from bn import LazyNet

def distr_to_mode(d):
	res = d.items()
	ml_key, ml_prob = res[0]
	for (k, v) in res:
		if v > ml_prob:
			ml_key, ml_prob = k, v
	return ml_key

# converts table to prob dist
def to_distr(t):
	rowdata = t.rows()
	values = map(lambda x: tuple(x.values()), rowdata)
	flat_vals = map(lambda e: e[0] if len(e) is 1 else e, values)
	return Dist(zip(flat_vals, t.probs))

from itertools import product
from digraph import adjs_to_edges

def generate_cpts(ln):
	def get_cpt(v,domains):
		cpt = None
		mydomain = None

		# make the cpt
		if v.dist is not None:
			cpt = dist_to_factor(v, v.dist)
			mydomain = v.dist.keys()
			domains[v] = mydomain
		else: 

			valid_args = [u for u in v.args]
			cpt = FactorTable(v, [v] + valid_args)
			doms = map(lambda x: domains[x], valid_args)
			# is the assigment consistent with naming.
			def is_consistent(obs):
				from digraph import edges_to_adjs
				obs_d = edges_to_adjs(obs)
				for v in obs_d.values():
					if len(set(v)) > 1:
						return False
				return True
			for x in product(*doms):
				r = v.eval(*x)
				if hasattr(r, 'dist') and r.dist is not None:
					for (val, prob) in r.dist.items():
						obs = zip([v] + valid_args, [val] + list(x))
						if is_consistent(obs):
							cpt.addObservation(dict(obs), prob)
				else:
					obs = zip([v] + valid_args, [r] + list(x))
					if is_consistent(obs):
						cpt.addObservation(dict(zip([v] + valid_args, [r] + list(x))), 1.0)

			mydomain = cpt.getDomain(v)
			domains[v] = mydomain
		return cpt

	string_ids = {}
	string_var_ids = {}

	domains = {}
	ordered_domains = {}
	var_cpt_map = {}

	vs = [v for v in ln.assn_order if type(v) is not Probability]

	assert(reduce(lambda x, y: x and y, map(lambda v: v.exact, vs)))

	for v in vs:
		var_cpt_map[v] = get_cpt(v, domains)
		string_ids[v] = "v" + str(id(v))
		string_var_ids[string_ids[v]] = v

	remove_probtype = lambda d: dict(filter(lambda (x, y): type(x) is not Probability, d.items()))
	domains = remove_probtype(domains)

	for (v, d) in domains.items():
		ordered_domains[v] = dict(zip(d,range(len(d))))

	ordered_domains = remove_probtype(ordered_domains)

	return (var_cpt_map, vs, ordered_domains, string_ids)

def all_exact(vs):
	return reduce(lambda x, y: x and y, map(lambda v: v.exact, vs))

# returns true if all args are independent of each other.
def independent(*args):
	N = LazyNet(args)
	G = N.graph

	def independence(a, b):
		if a == b:
			return False
		if len(a.args) == 0 and len(b.args) == 0:
			return True
		else:
			av = LazyNet((a,)).getvars()
			bv = LazyNet((b,)).getvars()
			return len(set(av).intersection(set(bv))) == 0			
	for i in range(len(args)):
		for j in range(i + 1, len(args)):
			if not independence(args[i], args[j]):
				return False
	return True

def debug_output(var, namespace={}):
	if namespace == {}:
		namespace = globals()

	N = var.getLN()
	sensible_dict = {}
	anon_index = 0
	for v in N.getvars():
		in_namespace = False
		var_func_name = "" if len(v.args) == 0 else "" if v.srcname == "" else " : " + v.srcname
		for (k, val) in namespace.items():
			if v is val:
				sensible_dict[v] = k + var_func_name
				in_namespace = True
		if not in_namespace:
			sensible_dict[v] = type(v).__name__ + str(anon_index) + var_func_name
			anon_index += 1


	graph_style = {'bgcolor': '"#061025"', 'fontcolor' : 'white'}
	node_style = {'shape': 'rectangle', 'fontname': 'VeraMono', 'color' : 'white', 'fontcolor' : 'white'}
	edge_style = {'color' : 'white'}

	return N.getNamedDigraph(sensible_dict).DOT(graph_style, node_style, edge_style)
