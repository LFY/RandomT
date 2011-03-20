from terms import App
from terms import Fmap
from terms import Bind

from interpreters import evalapp_bind
from interpreters import evalapp_bind_discrete
from interpreters import cleanEnv
from interpreters import sampleVar
from interpreters import jointSample
from interpreters import getCPTs

from syntax import mk_class_with_interface
from syntax import evalDExpr

from discrete_dist import Dist

def rfmap(f, interp=evalapp_bind):
    def call(*args):
        other_exprs = map(lambda e: e.expr, args)
        app_node = Fmap(f, *other_exprs)
        result = interp(app_node)
        return mk_class_with_interface(type(result), interp, Fmap)(app_node)
    return call

def rbind(f, interp=evalapp_bind):
    def call(*args):
        other_exprs = map(lambda e: e.expr, args)
        app_node = Bind(f, *other_exprs)
        result = interp(app_node)
        return mk_class_with_interface(type(result), interp, Fmap)(app_node)
    return call

def RndVar(gen, *args):
    return mk_class_with_interface(type(gen()), evalapp_bind, Fmap)(App(gen, *args))

def Pr(query, evidence, impl):
    eval_evidence = dict(map(lambda (k, v): (evalDExpr(k), v), evidence.items()))
    return impl(evalDExpr(query), eval_evidence)
