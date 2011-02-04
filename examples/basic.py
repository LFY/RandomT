from RandomT import *

# Random arithmetic

X = Flip()
Y = Flip()
Z = X + Y

print Pr(Z, {}, VarElim)
print Pr(Z, {}, RejectionSampler)

W = Z * Z + X

print Pr(W, {}, RejectionSampler)
print Pr(W, {}, VarElim)

W2 = Z * Z + Flip()

print Pr(W2, {}, RejectionSampler)
print Pr(W2, {}, VarElim)

# Calculate pi

from math import sqrt

X = Uniform(0, 1)
Y = Uniform(0, 1)
R = rnd(sqrt)(X * X + Y * Y)
print 4 * Pr({R : lambda r: r < 1}, {}, RejectionSampler)

# Works on classes

A = UniformString(["aaa", "abb", "abc"])

print sampleVar(A)
print sampleVar(A)
print sampleVar(A)

# "Inherit" methods from original class; 'replace' was automatically generated from str.replace
B = A.replace('a', 'b')

print sampleVar(B)
print sampleVar(B)
print sampleVar(B)
print sampleVar(B)

# Is a functional/probabilsitic dependency, i.e., condition on A makes sense
print Pr(B.count('b'), {}, VarElim)
print Pr(B.count('b'), {A : lambda s: s.endswith('c')}, VarElim)


