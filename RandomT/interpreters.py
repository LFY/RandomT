from util import *

from terms import Bind

from smallstep import store_bind_answer

from discrete_dist import Dist

from syntax import evalDExpr

def evalapp_bind(app_expr, env={}):
    return store_bind_answer(
            env,
            app_expr,
            map(lambda a: evalapp_bind(a, env), app_expr.args),
            inner_interp = evalDExpr,
            answer_interp = lambda sym, *args: sym.func(*args),
            is_bind = lambda sym: type(sym) == Bind)

from itertools import product

def gen_cpt_strict(sym, *_dists):
    dists = map(lambda d: d.data, _dists)
    if len(dists) == 0:
        return sym.func

    keys = list(set(_dists))

    dist_items = [(d, fsts(d.data.items())) if d.cond == False else (d, fsts(fsts(d.data.items()))) for d in keys]

    res = {}

    for vs in product(*snds(dist_items)):

        dist_vs = [(d, v) for (d, v) in zip(keys, vs)]

        dist_vs_dict = dict(dist_vs)

        vals = tuple(map(lambda d: dist_vs_dict[d], _dists))

        result_val = sym.func(*vals)

        res[(result_val, vals)] = res.get((result_val, vals), 0) + 1.0
    
    return Dist(res, conditional=True)

def evalapp_discrete_shallow(app_expr, env={}):
    return store_bind_answer(
            env, 
            app_expr,
            map(lambda a: evalapp_discrete_shallow(a, env), app_expr.args),
            inner_interp = lambda a: a,
            answer_interp = gen_cpt_strict,
            is_bind = lambda sym: type(sym) == Bind)

def flatten_cpt(dist):
    stage1 = map(lambda ((res, args), prob) : ((evalapp_discrete_shallow(res.expr).data.items(), args), prob), dist.data.items())
    stage2 = map(lambda ((items, args), prob) : map(lambda (v, p): ((v, args), prob * p), items), stage1)
    stage3 = concat(stage2)
    
    return Dist(dict(stage3), conditional=True)

def evalapp_bind_discrete(app_expr, env={}):
    return store_bind_answer(
            env,
            app_expr,
            map(lambda a: evalapp_bind_discrete(a, env), app_expr.args),
            inner_interp = flatten_cpt,
            answer_interp = gen_cpt_strict,
            is_bind = lambda sym: type(sym) == Bind)

def cleanEnv(env):
    return dict(map(lambda ((sym, vals), answer): (sym, answer), env.items()))
    
def sampleVar(abs_expr):
    res_env = {}
    return evalapp_bind(abs_expr.expr, res_env)

def getCPTs(abs_expr):
    res = {}
    evalapp_bind_discrete(abs_expr.expr, res)
    return cleanEnv(res)

def jointSample(abs_expr):
    res = {}
    evalapp_bind(abs_expr.expr, res)
    return cleanEnv(res)

def multi_eval_memo_store(app_exprs, interp=evalapp_bind):
    res_env = {}
    results = map(lambda a: interp(a, res_env), app_exprs)
    return (dict(zip(app_exprs, results)), res_env)

