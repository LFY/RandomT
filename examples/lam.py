from RandomT import *

from RandomT.terms import App, Fmap, Bind

X = Flip().expr
Y = Flip().expr

class Lam(object):
    def __init__(self, func):
        self.func = func


Xor1 = Lam(lambda X: Fmap(lambda x, y: x ^ y, X, Flip().expr))

Z = App(Xor1.func, X)

print evalapp_bind(Z)



