from randomt import Random, rnd
from randomlist import *
from monad import isFunction

class Function(object):
	def __init__(self, f):
		if isFunction(f):
			self.func = f
		elif type(f) is type(self):
			self.func = f.func
		
	def __call__(self, *args, **kwargs):
		rtval = self.func(*args, **kwargs)
		# Infect.
		if isFunction(rtval):
			return Function(rtval)
		else:
			return rtval

RandomF = Random(Function)

def Lam_Unit(func):
	return RandomF(lambda : Function(func))

@rnd 
def Lam(func):
	return RandomF(func)

@rnd
def App(func, *args, **kwargs):
	return func(*args, **kwargs)

@rnd 
def Filter(pred, xs):
	return RandomTuple(lambda : tuple(filter(pred, xs)))

@rnd 
def Map(func, xs):
	return RandomTuple(lambda : tuple(map(func, xs)))

@rnd
def Fold(func, xs):
	return RandomTuple(lambda : tuple(reduce(func, xs)))
