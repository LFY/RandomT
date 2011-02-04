
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

# NO
# def full_unwrap(x, unwrap):
#	v = unwrap(x)
#	while type(type(v)) is not type(type(1)):
		#v = unwrap(x)
#	return v

# Now this is not really a monad. This is a functor and 'join' :: m (m a) -> m a is _purposely_ left undefined until inference time
# At inference time, we collapse the 'tower' of Random(RandomT)'s that have formed--declaratively, over possibly different 'join' functions

# This is sort of a 'generic' way to write fmap given a:

# 'meta_class' to serve as...
# to use a construct_class function construct_class; the type constructor embodied
# the signature of fmap is (a -> b) -> f a -> f b
# fmap can be defined in terms of pure : a -> f a and exit : f a -> a

def fmap(func, meta_class, unwrap):
	def call(*args, **kwargs):
#		print 'call to %s with args %s' % (func.__name__, args)
		newargs = []
		for a in args:
			if type(type(a)) != meta_class:
				newargs.append(construct_class(type(a), meta_class)(a))
			else:
				newargs.append(a)

		# This runs the original function. It is assumed that the incoming arguments to the function return a meaningful value after 'unwrap' that will be compatible with the original function; it is assumed that func will return a meaningful value of type a that we then promote to type R a
		# The return value is only used to determine the type of the result
		rtval = func(*map(lambda x: unwrap(x), newargs))
		#print rtval

		# Determine type dynamically, requires a way to inhabit the type with 'unwrap'
		# This is interesting. Why doesn't this cahnge the behavior of meta, but breaks watersprinkler?
		# Ok, I see, it turns certain things into 'None'
		if type(type(rtval)) is meta_class:
			truetype = type(unwrap(rtval))
			def construction_function(*a, **aa):
				return func(*a, **aa)
			construction_function.__name__ = func.__name__ # Keep the name of the old function, for more meaningful debug outputs
			return construct_class(truetype, meta_class)(construction_function, *newargs, **kwargs)		
		def construction_function(*a, **aa):
			return func(*a, **aa)
		construction_function.__name__ = func.__name__
		#print 'newargs:'
		#print newargs
		#print 'done'

		newtype = construct_class(type(rtval), meta_class)

		#print newtype
		#print newtype.__init__

		#print "about to call the randomt constructor"
		
		return construct_class(type(rtval), meta_class)(construction_function, *newargs, **kwargs)
	call.__name__ = func.__name__
	return call
	
def stub():
	pass

def isFunction(f):
	return type(f) in (type(lambda: 1), type(int.__add__), type(stub))
