from util import *

from terms import Bind
from terms import Fail

from smallstep import store_bind_answer

from discrete_dist import Dist

from syntax import evalDExpr

def evalapp_memo(app_expr, env={}):
    return store_bind_answer(
            env,
            app_expr,
            map(lambda a: evalapp_bind(a, env), app_expr.args),
            inner_interp = None,
            answer_interp = lambda sym, *args: sym.func(*args),
            is_bind = lambda sym: False)

def evalapp_bind(app_expr, env={}):
    return store_bind_answer(
            env,
            app_expr,
            map(lambda a: evalapp_bind(a, env), app_expr.args),
            inner_interp = lambda e: evalapp_memo(evalDExpr(e)),
            answer_interp = lambda sym, *args: sym.func(*args),
            is_bind = lambda sym: type(sym) == Bind)

# An interpreter that fails early given an evidence query
unDE_evidence = lambda evidence: mapd(lambda (k, v): (evalDExpr(k), v), evidence)

def check_evidence(v, val, evidence):
    if evidence.has_key(v):
        if isfunction(evidence[v]):
            return evidence[v](val)
        else:
            return val == evidence[v]
    else:
        return True

def inconsistent(env, evidence):
    cleaned = cleanEnv(env)
    res = not conj(map(lambda (k, v): check_evidence(k, v, evidence), cleaned.items()))
    return res


def evalapp_bind_evidence(app_expr, evidence, env={}):
    # Note that in order to work correctly, evalapp_bind_evidence needs to also
    # evaluate the variables in evidence 

    # Question: What is the best order, if any?

    uneval = filter(lambda k: k not in env.keys() and app_expr != k, evidence.keys())

    early_answers = map(lambda k: evalapp_bind_evidence_partial(k, evidence,env), uneval)

    for a in early_answers:
        if type(a) == Fail:
            return a

    return evalapp_bind_evidence_partial(app_expr, evidence, env)



def evalapp_bind_evidence_partial(app_expr, evidence, env={}):

    # First check for failure: if the environment is already inconsistent

    if inconsistent(env, evidence):
        return Fail(env)

    # Propagate failed computations without running small-step evaluator

    answers = map(lambda a: evalapp_bind_evidence_partial(a, evidence, env), app_expr.args)
    for a in answers:
        if type(a) == Fail:
            return a

    result = store_bind_answer(
                env,
                app_expr,
                answers,
                inner_interp = evalDExpr,
                answer_interp = lambda sym, *args: sym.func(*args),
                is_bind = lambda sym: type(sym) == Bind)

    # Second check for failure: if the environment after calculating app_expr
    # is inconsistent

    if inconsistent(env, evidence):
        return Fail(env)

    return result

# Discrete distributions: strictly specified probability tables

from cpt_ops import gen_cpt_strict

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

