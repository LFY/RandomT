from util import *

def condition_cpt(cpt):
    pass

from discrete_dist import Dist
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

