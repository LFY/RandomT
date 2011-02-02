from RandomT import *

# How do we flatten?

X = Flip(0.2)
Y = Flip(0.3)

RRInt = Random(Random(int))

Z = RRInt(Dist({X : 0.5, Y : 0.5}))

print sampleVar(Z)
print sampleVar(Z)
print sampleVar(Z)
print sampleVar(Z)
print sampleVar(sampleVar(Z))
print sampleVar(sampleVar(Z))
print sampleVar(sampleVar(Z))
print sampleVar(sampleVar(Z))
print sampleVar(sampleVar(Z))
#print Pr(Z, {}, RejectionSampler)
#print Pr(Z, {}, RejectionSampler)
#print Pr(Z, {}, RejectionSampler)
#print Pr(Z, {}, RejectionSampler)
#print Pr(Z, {}, RejectionSampler)
#print Pr(Z, {}, RejectionSampler)

print Pr(Z)
print Pr(Flip())
X = Flip()
Y = Flip()
Z = X + Y
print Pr(X + Y, {}, VarElim)

Z = Uniform(2, 3)
print sampleVar(Z)
print Pr({Z : lambda x: x < 2.5}, {}, RejectionSampler)
