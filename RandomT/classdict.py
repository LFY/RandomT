# Methods for transforming dictionaries and class dictionaries.

# Filters out elements of the dictionary d, where f((key, value)) is a boolean function that specifies which ones to keep (True)
def dict_filter(d, f):
	return dict(filter(f, d.items()))

# Add/Replaces elements of the dictionary d with another dictionary.
def dict_add(d, a):
	res = dict(d)
	res.update(a)
	return res

# Map: transforms elements of the dictionary d with a function f((key, value)) -> (key, value)
def dict_map(d, f):
	return dict(map(f, d.items()))

class DictOp(object):
	def __init__(self, func, arg):
		self.op = lambda d: func(d, arg)
	def __call__(self, d):
		return self.op(d)
		
# DictTransform: Initialized by a sequence of functions denoting the transformations, with left args being applied first.
class DictTransform(object):
	def __init__(self, *args):
		for a in args:
			assert(callable(a))
		self.transforms = args
	def __call__(self, d):
		r = dict(d)
		for t in self.transforms:
			r = t(r)
		return r

# Basic unit test.
def basic_dict_transform_test():
	a = {}
	a[0] = 1
	a[1] = 2
	a[2] = 3
	
	print a
	print dict_filter(a, lambda (k, v): True if k is 0 else False)
	print dict_filter(a, lambda (k, v): True if k > 0 else False)
	
	b = {}
	b[0] = 5
	b[3] = 6
	
	print b
	print dict_add(a, b)
	
	print dict_map(dict_add(a, b), lambda (k, v): (k + 1, v + 1))
	
	T = DictTransform(lambda d: dict_add(d, b), lambda d: dict_map(d, lambda (k, v): (k + 1, v + 1)))
	
	print T(a)
	
	AddB = DictOp(dict_add, b)
	MapAddOne = DictOp(dict_map, lambda (k, v): (k + 1, v + 1))
	
	T = DictTransform(AddB, MapAddOne)
	
	print T(a)

# Restricts values based on type.
class DictTypeFilter(DictOp):
	def __init__(self, *types):
		def filter_types((k, v)):
			for t in types:
				if type(v) is t:
					return True
			return False
		self.op = lambda d: dict_filter(d, filter_types)
		
# Filters by key.	
class DictExcludeKeys(DictOp):
	def __init__(self, *keys):
		def filter_func((k, v)):
			for key in keys:
				if k == key:
					return False
			return True
		self.op = lambda d: dict_filter(d, filter_func)
	
# Transforms values based on a function.
class DictValueMap(DictOp):
	def __init__(self, f):
		self.op = lambda d: dict_map(d, lambda (k, v): (k, f(v)))

def highlevel_dict_transform_test():
	a = { 0: 1, 1: 'test'}
	StringsOnly = DictTypeFilter(str)
	print StringsOnly(a)
	
	a = { 0: 1, 1: 2, 2: 3}
	AddOne = DictValueMap(lambda x: x + 1)
	print AddOne(a)
	NoZero = DictExcludeKeys(0, 1, 2)
	print NoZero(a)

# More specific dictionary ops.
from types import FunctionType

# Restricts to method types.
class MethodRestrictor(DictOp):
	def __init__(self):
		self.op = DictTypeFilter(FunctionType, type(int.__add__), type(list.insert))

# Restricts to non-metadata dictionary entries. __str__ and __repr__ are in there because of print.
class MetaPropertyExcluder(DictOp):
	def __init__(self):
		self.op = DictExcludeKeys('__getattribute__', '__getformat__', '__repr__', '__str__')
	
def classdict_transform_test():
	d = int.__dict__
	
	print MethodRestrictor()(d)
	print MetaPropertyExcluder()(d).items()

if __name__ == '__main__':
	basic_dict_transform_test()
	highlevel_dict_transform_test()
	classdict_transform_test()
	
	