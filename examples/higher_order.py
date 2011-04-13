from RandomT import *

# Wrapper class for functions

class Func(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, *args):
        return self.f(*args)

# One representation is to consider a discrete collection of functions.
# This is essentially enumerating an entire space of functions.

f1 = Func(lambda x: x + 1)
f2 = Func(lambda x: x + 2)
f3 = Func(lambda x: x + 1)

# f1 and f3 are intensionally unequal by Python's object construction semantics

# f1 and f3 are extensionally equal

# In order for results to make sense, 

F = RndVar(Dist({f1 : 0.5, f2 : 0.5, f3 : 0.5}))

T = RndVar(Dist({1 : 1.0}))

X = F(T)

print Pr(F, {X : 2}, rejectionN(100))

# We can also consider the parameterization of a function space by a random variable:

@rfmap
def G(x):
    return Func(lambda n: n + x)

X = Flip(0.5)
Y = G(X) # Y is a random function
Z = Y(T)

# Consider random map (order-2 function)

Map = rfmap(map)

L = RndVar(Dist({(1, 2, 3, 4, 5) : 1.0}))

Z = Map(G(X), L)

print sampleVar(Z)
print sampleVar(Z)
print sampleVar(Z)
print sampleVar(Z)

# And fold

Fold = rfmap(reduce)

H = rfmap(lambda z: Func(lambda x, y: x + y + z))

Z = Fold(H(X), L)

print sampleVar(Z)
print sampleVar(Z)
print sampleVar(Z)
print sampleVar(Z)


