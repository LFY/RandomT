from util import *

class Dist(object):
    def __init__(self, data, conditional=False):
        self.cond = conditional
        self.data = data
    def pr(self, *args):
        if not self.cond:
            if len(args) == 0:
                return Dist(self.data)
            else:
                return 0.0 if not self.data.has_key(args[0]) else self.data[args[0]]
        else:
            consistent_data = map(lambda ((v, vals), prob): (v, prob), filter(lambda ((v, vals), prob): vals == args, self.data.items()))
            return Dist(accum_dict(consistent_data))
    def norm(self,):
        self.data = norm_dict(data)
        return self
    def __call__(self, *args):
        return self.sample(*args)
    def sample(self,*args):
        t = uniform(0,1)
        probs = [v for (k, v) in self.data.items()]
        vals = [k for (k, v) in self.data.items()]
        ind = 0
                        
        for i in range(len(probs)):
            if i is not 0:
                probs[i] = probs[i] + probs[i - 1]
        for i in range(len(probs)):
            if t < probs[i]:
                ind = i
                break                
        return vals[ind]
    def __repr__(self):
        return "Dist %s" % self.data if not self.cond else "CPT %s" % self.data

