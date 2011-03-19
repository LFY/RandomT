from RandomT import *


X, Y, Z = Flip(), Flip(), Flip()

F = rbind(lambda x: Y if x == 1 else (Z + Y))

W = F(X)

print Pr(W, {}, RejectionSampler)
