from RandomT import *

@rnd
def Grass(x, y):
	if x == 1 and y == 1:
		return Flip(0.99)
	elif x == 0 and y == 1:
		return Flip(0.9)
	elif x == 1 and y == 0:
		return Flip(0.9)
	elif x == 0 and y == 0:
		return Flip(0.0)

# Ah, this bug, where if we use a switch-style function and apply 'rnd' to it and if not every path through the function results in a return value....
@rnd
def Sprinkler(x):
	if x == 1:
		return Flip(0.5)
	elif x == 0:
		return Flip(0.1)

@rnd
def Rain(x):
	if x == 1:
		return Flip(0.2)
	elif x == 0:
		return Flip(0.8)

C = Flip(0.5)

print "BEGIN PROBLEM LINE"
S = Sprinkler(C)

R = Rain(C)

W = Grass(S, R)

print Pr(W)

print debug_output(W, locals())
