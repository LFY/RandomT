# The small-step evaluator for monadic expressions

def store_bind_answer(
        env,
        sym,
        vals,
        inner_interp,
        answer_interp,
        is_bind):
    if not env.has_key((sym, tuple(vals))):
        answer = answer_interp(sym, *vals)
        if is_bind(sym):
            true_answer = inner_interp(answer)
            env[(sym, tuple(vals))] = true_answer
        else:
            env[(sym, tuple(vals))] = answer
    return env[(sym, tuple(vals))]

# Basic memoizing small-step evaluator

def store(env, sym, vals=[]):
    if not env.has_key((sym, tuple(vals))):
        env[(sym, tuple(vals))] = sym.func(*vals)
    return env[(sym, tuple(vals))]

