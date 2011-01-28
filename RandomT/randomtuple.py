from randomt import Random
from randomt import rnd

RandomTuple = Random(tuple)

def joint(*a):
	return tuple(a)

Joint = rnd(joint)