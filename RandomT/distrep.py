from random import uniform

def normalize(xs):
	s = float(sum(xs))
	if s == 0:
		return map(lambda x: 1.0 / len(xs), xs)
	return map(lambda x: x / s, xs)
class Dist(dict):
	def __init__(self, *args):
		dict.__init__(self, *args)
		self.exact = True
		kv = zip(*self.items())
		kv[1] = normalize(kv[1])
		kv = zip(*kv)
		dict.__init__(self, kv)
	def combine(self, src, *args):
		pass
	def sample(self,*args):
		t = uniform(0,1)
		probs = [v for (k, v) in self.items()]
		vals = [k for (k, v) in self.items()]
		ind = 0
						
		for i in range(len(probs)):
			if i is not 0:
				probs[i] = probs[i] + probs[i - 1]
		for i in range(len(probs)):
			if t < probs[i]:
				ind = i
				break				
		return vals[ind]


