from RandomT import *
from RandomT.interpreters import evalapp_bind_evidence

from pprint import *

X = Flip()
Y = Flip()

Z = rfmap(lambda x, y: x and y)(X, Y)

W = X ^ Y

env = {}

print 'Z = X and Y. Running this expression conditioned on X = True with an interpreter that gives up as soon as the sample is inconsistent:'

print 'X',X.expr
print 'Y',Y.expr
print 'Z',Z.expr
print 'W',W.expr

print 'answer',evalapp_bind_evidence(Z.expr, {W.expr : True}, env)

print 'evaluated env'

pprint(env)

