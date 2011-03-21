from randomt import *

Flip = lambda p = 0.5: RndVar(Dist({True : float(p), False : 1 - float(p)}))
Binary = lambda p = 0.5: RndVar(Dist({1 : float(p), 0 : 1 - float(p)}))


from random import uniform

Uniform = lambda a = 0, b = 1: RndVar(lambda : uniform(a, b))

Multinom = lambda d: RndVar(Dist(d))

Selection = lambda xs: RndVar(Dist(dict(map(lambda x: (x, 1.0), xs))).norm())

Constant = lambda x: RndVar(Dist({x : 1.0}))

from random import gauss

Gaussian = lambda m, v: RndVar(lambda : gauss(m, v))
