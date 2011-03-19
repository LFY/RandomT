def MH(asn, score, proposal, accept):
    curr_asn = asn
    next_asn = asn

    curr_score = score(asn)
    next_score = score(asn)

    while True:

        next_asn = proposal(curr_asn)
        next_score = score(next_asn)

        if accept(next_score, curr_score):
            curr_asn, curr_score = next_asn, next_score
        
        yield curr_asn, curr_score

