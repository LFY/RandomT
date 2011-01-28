# Based on http://www.python.org/do/essays/graphs

# directed graph
class Digraph(object):
	def __init__(self, d):
		for (k, v) in d.items():
			assert(type(v) is list or type(v) is tuple)
		self.rep = d
		
		# keep track of the reverse relations for speed.
		self.rev_rep = edges_to_adjs(map(lambda (x, y): (y, x), adjs_to_edges(d)))
			
	def verts(self,):
		return [k for (k, v) in self.rep.items()]
	def children(self, v):
		return self.rep[v] if self.rep.has_key(v) else []
	def parents(self, v):
		return self.rev_rep[v] if self.rev_rep.has_key(v) else []
	def reverse(self,):
		return Digraph(self.rev_rep)
	def __repr__(self,):
		res = ""
		for (a, bs) in self.rep.items():
			for b in bs:
				res = res + "%s -> %s\n" % (a, b)
		return res
	def without_edge(self, e):
		without_key = e[0]
		without_val = e[1]
		new_rep = {}
		for (k, v) in self.rep.items():
			if k == without_key:
				new_rep[k] = filter(lambda v: v != without_val, self.rep[k])
			else:
				new_rep[k] = v
		
#		if len(new_rep[k]) == 0:
#			del new_rep[k]
		return Digraph(new_rep)
		
	def DOT(self,graphprop={},nodeprop={},edgeprop={}):
		def dot_file(s):
			return "digraph G {\n" + s + "}"
		
		def adj_list():
			res = ""
			for (k, vs) in self.rep.items():
				for v in vs:
					res += "\"%s\" -> \"%s\"\n" % (k, v)
			return res
		
		def properties():
			def prop_form(d):
				res = "["
				for (k, v) in d.items():
					res += "%s=%s " % (k, v)
				res += "]"
				return res
				
			return "graph " + prop_form(graphprop) + '\n' + "node " + prop_form(nodeprop) + '\n' + "edge " + prop_form(edgeprop)
		
		return dot_file(properties() + adj_list())

def merge_digraph(a, b):
	newdict = dict(a.rep)
	newdict.update(b.rep)
	for (k, v) in newdict.items():
		newdict[k] = list(set(a.rep[k]).union(set(b.rep[k])))
		
	return Digraph(newdict)
	
def adjs_to_edges(d):
	res = []
	for (k, vs) in d.items():
		for v in vs:
			res.append((k, v))
	return res
	
def edges_to_adjs(es):
	rep = {}
	for e in es:
		if not rep.has_key(e[0]):
			rep[e[0]] = []
		
		rep[e[0]].append(e[1])
	
	return rep
	

def shortest_path(graph, start, end, path=[]):
	path = path + [start]
	if start == end:
		return path
	if not graph.has_key(start):
		return []
	shortest = []
	for node in graph[start]:
		if node not in path:
			newpath = shortest_path(graph, node, end, path)
			if newpath:
				if not shortest or len(newpath) < len(shortest):
					shortest = newpath
	return shortest

def top_sort(graph):
	S = filter(lambda s: len(graph.parents(s)) == 0, graph.verts())
	L = []
	while len(S) > 0:
		n = S.pop()
		L.append(n)
		to_remove = []
		for v in graph.children(n):
			graph = graph.without_edge((n, v))
			if len(graph.parents(v)) == 0:
				S.append(v)
	if len(adjs_to_edges(graph.rep)) > 0:
		raise Exception("No topological sort exists.")
	return L

if __name__ == '__main__':
	graph_dict = {1 : [2, 3], 2 : [3, 4], 3 : [4], 4: [3], 5 : [6], 6: [3]}
	A = Digraph(graph_dict)
	
	print A.DOT()
	print A.verts()
	print A.children(1)
	print A.children(2)
	print A.children(3)
	print A.children(4)
	print A.children(5)
	print A.children(6)
	print A.parents(6)
	print A.parents(3)
	
	print A.rep
	print A.rev_rep
	
	print Digraph(A.rev_rep).rep
	
	#print adjs_to_edges(A.rep)
	#print adjs_to_edges(A.rev_rep)
	
	print shortest_path(A.rep, 1, 4)
	
	B = {0: [1, 2], 1: [3, 4], 2: [3, 4]}
	print top_sort(Digraph(B))
	print top_sort(A)
	
