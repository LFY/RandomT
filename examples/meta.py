from RandomT import *


X = Flip(0.2)
Y = Flip(0.3)

RRInt = Random(Random(int))

Z = RRInt(Dist({X : 0.5, Y : 0.5}))

print Z.sample()
print Z.sample()
print Z.sample()
print Z.sample()
print Z.sample()
print Z.sample()
print Z.sample()
print Z.sample()

print Pr(Z)
print Pr(Flip())
X = Flip()
Y = Flip()
Z = X + Y
print Pr(X + Y, {}, VarElim)

Z = Uniform(2, 3)
print Z.sample()
print Pr({Z : lambda x: x < 2.5}, {}, RejectionSampler)
