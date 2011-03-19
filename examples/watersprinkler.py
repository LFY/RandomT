from RandomT import *

Flip = lambda p: RndVar(Dist({1 : p, 0 : 1 - p}))

@rbind
def GrassWet(x, y):
	if x == 1 and y == 1:
		return Flip(0.99)
	elif x == 0 and y == 1:
		return Flip(0.9)
	elif x == 1 and y == 0:
		return Flip(0.9)
	elif x == 0 and y == 0:
		return Flip(0.0)

@rbind
def Sprinkler(x):
	if x == 1:
		return Flip(0.5)
	elif x == 0:
		return Flip(0.1)

@rbind
def Rain(x):
	if x == 1:
		return Flip(0.2)
	elif x == 0:
		return Flip(0.8)

C = Flip(0.5)
S = Sprinkler(C)
R = Rain(C)
W = GrassWet(S, R)

print Pr(W, {}, VarElim) 

print Pr(S, {W : 1, R: 0}, VarElim)
print Pr(W, {}, RejectionSampler) 

print debug_output(W, locals())

print 'another way to specify'

Cloudy = Flip(0.5)
Wet = GrassWet(Sprinkler(Cloudy), Rain(Cloudy))

print Pr(Wet, {}, VarElim)
