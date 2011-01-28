from randomt import Random, rnd
from randomlist import *

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

@rnd
def Lam(func):
	return RandomF(lambda : func)

@rnd
def App(func, *args, **kwargs):
	return func(*args, **kwargs)


