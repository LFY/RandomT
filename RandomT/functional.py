
classcache = {}

# Simulating type constructors

def construct_class(base_type, meta_class):
	name = meta_class.__name__ + base_type.__name__
	if not classcache.has_key(name):
		classcache[name] = meta_class(name, (base_type,), {})
	return classcache[name]
	
def construct_with_bases(c, meta):
	name = meta.__name__ + c.__name__
	if not classcache.has_key(name):
		return type.__new__(meta, meta.__name__ + c.__name__, tuple([construct_with_bases(b, meta) for b in c.__bases__ if b is not object]), dict(construct_class(c, meta).__dict__))
	else:
		return classcache[name]

def bind(func, meta_class, unwrap):
	def call(*args, **kwargs):
		newargs = []
		for a in args:
			if type(type(a)) != meta_class:
				newargs.append(construct_class(type(a), meta_class)(a))
			else:
				newargs.append(a)
		rtval = func(*map(lambda x: unwrap(x), newargs))
		truetype = type(unwrap(rtval))
		def construction_function(*a, **aa):
			return func(*a, **aa)
		construction_function.__name__ = func.__name__ 
		return construct_class(truetype, meta_class)(construction_function, *newargs, **kwargs)		
	call.__name__ = func.__name__
	return call

def fmap(func, meta_class, unwrap):
	def call(*args, **kwargs):
		newargs = []
		for a in args:
			if type(type(a)) != meta_class:
				newargs.append(construct_class(type(a), meta_class)(a))
			else:
				newargs.append(a)
		rtval = func(*map(lambda x: unwrap(x), newargs))
		def construction_function(*a, **aa):
			return func(*a, **aa)
		construction_function.__name__ = func.__name__
		newtype = construct_class(type(rtval), meta_class)
		return construct_class(type(rtval), meta_class)(construction_function, *newargs, **kwargs)
	call.__name__ = func.__name__
	return call
	
def stub():
	pass

def isFunction(f):
	return type(f) in (type(lambda: 1), type(int.__add__), type(stub))
