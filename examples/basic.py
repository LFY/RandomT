from RandomT import *
from pprint import pprint

# Deterministic function lifting

def very_basic():

    # Flip: { True: 0.5, False: 0.5 }

    X = Flip()
    Y = Flip()
    Z = X & Y

    print Pr(Z) # { True: 0.25, False: 0.75 }


    print 'basic CPTs:'
    print getCPTs(Z)

very_basic()

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
    print A[True] * 4 # ~3.14

    # Normal program

    A = 0
    N = 1000
    for i in range(N):
     x = uniform(0,1)
     y = uniform(0,1)
     r = sqrt(x * x + y * y)
     if r < 1.0:
         A += 4 * 1.0 / N
    print A # ~3.14

test()

def logic():
    Eq = rfmap(lambda a, b: a == b)

    # For the daily schedule for Monday to Wednesday:
    ndays = 3

    # One of the days I'll shop.
    Shop = Selection(*range(ndays))

    # One of the days I'll take a walk.
    Walk = Selection(*range(ndays))

    # One of the days I'll go to the barber.
    Barber = Selection(*range(ndays))

    # One of the days I'll go to the supermarket.
    Super = Selection(*range(ndays))

    # ...

    # The same day as I go to the supermarket, I'll shop.
    SuperShop = Eq(Shop, Super)

    # The same day as I talk a walk I'll go to the barber.
    WalkBarber = Eq(Walk, Barber)

    # I'll go to the supermarket the day 
    # before the day I'll take a walk.
    SuperWalk = Eq(Super, Walk - 1)

    # I'll take a walk Tuesday.
    TuesWalk = Eq(Walk, 1)

    # ...

    All = Tuple(Shop, Walk, Barber, Super)
    
    consistent = {
            SuperShop : True,
            WalkBarber : True,
            SuperWalk : True,
            TuesWalk : True}

    print Pr(All, consistent) # {(0, 1, 1, 0) : 1.0}

logic()

