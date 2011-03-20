from RandomT import *
from RandomT.interpreters import evalapp_bind_evidence


X = Flip()
Y = Flip()

Z = rfmap(lambda x, y: x and y)(X, Y)


env = {}
print 'X',X.expr
print 'Y',Y.expr
print 'Z',Z.expr
print 'answer',evalapp_bind_evidence(Z.expr, {X : True}, env)
print 'evaluated env',env

