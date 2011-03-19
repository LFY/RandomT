from util import *
from interpreters import *


def rejectionsampler(query, evidence, samples, interp=lambda vs: multi_eval_memo_store(vs)[0]):
    all_vars = [query] + evidence.keys()

    def check_evidence(v, val):
        if evidence.has_key(v):
            if isfunction(evidence[v]):
                return evidence[v](val)
            else:
                return val == evidence[v]
        else:
            return True
    
    conjunction = lambda bs: reduce(lambda x, y: x and y, bs, True)
    satisfy_evidence = lambda var_answrs: conjunction(
            map(lambda (v, a): check_evidence(v, a),
                var_answrs.items()))

    def filter_relevant(d):
        res = {}
        for (k, v) in d.items():
            if k in all_vars:
                res[k] = v
        return res

    results = map(lambda vs: interp(vs), [all_vars] * samples)
    consistent_results = filter(lambda var_answrs: satisfy_evidence(var_answrs), results)
    consistent_query = map(lambda var_answrs: (var_answrs[query], 1.0), consistent_results)

    return norm_dict(accum_dict(consistent_query))

rejectionN = lambda n: lambda query, evidence: rejectionsampler(query, evidence, n)

