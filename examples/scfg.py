from RandomT import *
from RandomT.bnt import BNTEngine

Start = UniformString(['S'])

def applyN(f, n):
	if n == 1:
		return lambda *a, **aa: f(*a, **aa)
	else:
		return lambda *a, **aa: f(applyN(f, n - 1)(*a, **aa))

def transform_string(base, shell):
	res = ""
	for i in shell:
		if i == "S":
			res += base
		else:
			res += i
	return res

def transform_string_one_nt(base, shell):
	trans = False
	res = ""
	for i in shell:
		if trans == False:
			if i == "S":
				res += base
			else:
				res += i
			trans = True
		else:
			res += i
	return res

TransformString = rnd(transform_string)
		
Trans = lambda S: TransformString(S, UniformString(["SS", "+S-", "+-"]))

SomeString = applyN(Trans, 10)(Start)

print debug_output(SomeString, locals())
print Pr(SomeString, {}, BNTEngine)
#print Pr(SomeString)
