from random import uniform
from random import randint

filterd = lambda pred, d: dict(filter(pred, d.items()))

filterdk = lambda pred, d: filterd(lambda (k, v): pred(k), d)
filterdv = lambda pred, d: filterd(lambda (k, v): pred(v), d)

mapd = lambda f, d: dict(map(f, d.items()))

mapdk = lambda f, d: mapd(lambda (k, v): (f(k), v), d)
mapdv = lambda f, d: mapd(lambda (k, v): (k, f(v)), d)

disj = lambda xs: reduce(lambda x, y: x or y, xs, False)
conj = lambda xs: reduce(lambda x, y: x and y, xs, True)

def normalize(xs):
    s = float(sum(xs))
    if s == 0:
        return map(lambda x: 1.0 / len(xs), xs)
    return map(lambda x: x / s, xs)

def accum_dict(xys, zero=0, binop = lambda x, y: x + y):
    res = {}
    for (k, v) in xys:
        res[k] = binop(res.get(k, zero), v)
    return res

def norm_dict(d):
    total = float(sum(d.values()))
    return dict(map(lambda (k, v): (k, v / total), d.items()))

snds = lambda xys: map(lambda (x, y): y, xys)
fsts = lambda xys: map(lambda (x, y): x, xys)

nub = lambda xs: list(set(xs))


