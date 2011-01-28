import inspect


def nosy(func):
	def call(*args, **kwargs):
		print inspect.getargvalues(inspect.currentframe())
		return func(*args, **kwargs)
	return call

@nosy
def recurse(limit):
	local_variable = '.' * limit
	if limit <= 0:
		return
	recurse(limit - 1)
	return


from realfunc import *

@nosy