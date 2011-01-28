# Monadic computations in Python.

classcache = {}

# construct_class a :: a -> M a

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


def full_unwrap(x, unwrap):
	v = unwrap(x)
	while type(type(v)) is not type(type(1)):
		v = unwrap(x)
	return v
	
# bind :: (a -> M b) -> M a -> (M a -> M b)
# bind_fmap :: (a -> b) -> M a -> (M a -> M b)

def bind(func, meta_class, unwrap):
	def call(*args, **kwargs):
#		print 'call to %s with args %s' % (func.__name__, args)
		newargs = []
		for a in args:
			if type(type(a)) != meta_class:
				newargs.append(construct_class(type(a), meta_class)(a))
			else:
				newargs.append(a)
#		print 'initial type test'
		rtval = func(*map(lambda x: full_unwrap(x, unwrap), newargs))
#		truetype = get_base_type(rtval, meta_class, unwrap)
#		print 'end initial type test'
		# Flattening
		if type(type(rtval)) is meta_class:
			truetype = type(unwrap(rtval))
			def construction_function(*a, **aa):
				return func(*a, **aa)
			construction_function.__name__ = func.__name__
			return construct_class(truetype, meta_class)(construction_function, *newargs, **kwargs)		
		def construction_function(*a, **aa):
			return func(*a, **aa)
		construction_function.__name__ = func.__name__
		return construct_class(type(rtval), meta_class)(construction_function, *newargs, **kwargs)
	call.__name__ = func.__name__
	return call
	
def stub():
	pass

def isFunction(f):
	return type(f) in (type(lambda: 1), type(int.__add__), type(stub))
