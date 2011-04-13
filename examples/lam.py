from RandomT import *

from RandomT.terms import App, Fmap, Bind

X = Flip().expr
Y = Flip().expr

class Lam(object):
    def __init__(self, func):
        self.func = func
    def __call__(self, *args):
        return self.func(*args)

class Fix(object):
    def __init__(self, func):
        self.func = func

Xor1 = Lam(lambda X: Fmap(lambda x, y: x ^ y, X, Flip().expr)) 

Z = App(Xor1, X)

def store1(env, sym, vals=[]):
    if not env.has_key((sym, tuple(vals))):
        env[(sym, tuple(vals))] = sym.func(*vals)
    return env[(sym, tuple(vals))]

eval1 = lambda expr, env = {} : store1(
            env,
            expr,
            map(lambda e: eval1(e, env), expr.args))

print eval1(Z)

# The question is, how to do Pr(Xor1 | X), Pr(X | Xor1 == f) ?

# We can consider several approaches for tackling this problem.


