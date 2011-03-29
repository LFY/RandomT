from random import uniform
from random import randint
from inspect import isfunction

# Extra dictionary operations

# pred :: (k, v) -> bool

filterd = lambda pred, d: dict(filter(pred, d.items()))

filterdk = lambda pred, d: filterd(lambda (k, v): pred(k), d)
filterdv = lambda pred, d: filterd(lambda (k, v): pred(v), d)

# f : (k, v) -> t

mapd = lambda f, d: dict(map(f, d.items()))

mapdk = lambda f, d: mapd(lambda (k, v): (f(k), v), d)
mapdv = lambda f, d: mapd(lambda (k, v): (k, f(v)), d)

disj = lambda xs: reduce(lambda x, y: x or y, xs, False)
conj = lambda xs: reduce(lambda x, y: x and y, xs, True)

# acc :: (k, v) -> (k, v) -> (k, v)

reduced = lambda acc, d, zero={}: dict(reduce(acc, d.items(), {}))

def accum_dict(xys, zero=0, binop = lambda x, y: x + y):
    res = {}
    for (k, v) in xys:
        res[k] = binop(res.get(k, zero), v)
    return res


# Extra list operations

snds = lambda xys: map(lambda (x, y): y, xys)
fsts = lambda xys: map(lambda (x, y): x, xys)

nths = lambda xs, n: map(lambda ts: ts[n], xs)

nub = lambda xs: list(set(xs))
concat = lambda xss: reduce(lambda x, y: x + y, xss, [])

# Vector operations

def normalize(xs):
    s = float(sum(xs))
    if s == 0:
        return map(lambda x: 1.0 / len(xs), xs)
    return map(lambda x: x / s, xs)

def norm_dict(d):
    total = float(sum(d.values()))
    return dict(map(lambda (k, v): (k, v / total), d.items()))

# Ranges

interp_range = lambda min, max, n: map(lambda i: min + (float(i) / (n - 1)) * float(max - min), range(n))

meshgrid = lambda xs, ys: ([xs] * len(ys), zip(*([ys] * len(xs))))

coordgrid = lambda mesh: map(lambda cs: zip(*cs), zip(*mesh))

