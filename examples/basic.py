from RandomT import *

# Deterministic function lifting

flip = lambda p = 0.5 : RndVar(Dist({0 : 1 - float(p), 1 : float(p)}))

X = flip()
Y = flip()
Z = X + Y

print Pr(Z, {}, rejectionN(50))

print getCPTs(Z)

randstr = lambda : RndVar(Dist({"ABC" : 0.5, "abc" : 0.5}))

X = randstr()
Y = randstr().lower()
Eq = rfmap(lambda x, y: x == y)(X, Y)

print Pr(X, {Eq : True}, rejectionN(50))

# Conditional distributions

F = rbind(lambda x: flip(0.2) if x else flip(0.8))

print sampleVar(F(X))
print getCPTs(F(X))

print sampleVar(F(F(X)))
print getCPTs(F(F(X)))

print Pr(F(X), {}, rejectionN(50))
