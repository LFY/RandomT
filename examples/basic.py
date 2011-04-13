from RandomT import *
from pprint import pprint

# Deterministic function lifting

flip = lambda p = 0.5 : RndVar(Dist({0 : 1 - float(p), 1 : float(p)}))

X = flip()
Y = flip()
Z = X + Y

print Pr(Z, {}, rejectionN(50))

pprint(getCPTs(Z))

randstr = lambda : RndVar(Dist({"ABC" : 0.5, "abc" : 0.5}))

X = randstr()
Y = randstr().lower()
Eq = rfmap(lambda x, y: x == y)(X, Y)

print Pr(X, {Eq : True}, rejectionN(50))

# Conditional distributions

F = rbind(lambda x: flip(0.2) if x else flip(0.8))

print sampleVar(F(X))
pprint(getCPTs(F(X)))

print sampleVar(F(F(X)))
pprint(getCPTs(F(F(X))))

print Pr(F(X), {}, rejectionN(50))


# Pi

from random import uniform
from math import *

Uniform = lambda a, b: RndVar(lambda : uniform(a, b))
Sqrt = rfmap(sqrt)

def test():

    X = Uniform(0,1)
    Y = Uniform(0,1)
    R = Sqrt(X * X + Y * Y)

    A = Pr(R < 1.0) 
    print A[True] * 4

    # Normal program

    A = 0
    N = 1000
    for i in range(N):
     x = uniform(0,1)
     y = uniform(0,1)
     r = sqrt(x * x + y * y)
     if r < 1:
         A += 4 * 1.0 / N
    print A

test()
