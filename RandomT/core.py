# Python monadic computations: method chaining as do-notation

from classdict import *

classcache = {}

# m is a formal type constructor; represented here as a Python class with internal value self.val
# Given a monad or an applicative functor, liftM or fmap the class methods.

# By applicative functor m, we usually mean it has a return, fmap and apply:
# mreturn : a -> m a
# fmap: (a - > b) -> m a -> m b
# apply: m (a -> b) -> m a -> m b
# If m is also a monad, there is a function
# mbind: m a -> (a -> m b) -> m b

# Auto-derive a set of methods for m basetype.
# If we give an fmap argument, we assume m is an applicative functor.
# Else, m is a monad.
def liftM(f, ret, bind):
	returned = lambda *args: ret(f(*args))
	return lambda *margs: bind(returned, *margs)
def class_transform(name, basetype, mreturn, bind=None, fmap=None):
	class monad_wrapper(object):
		# Takes in a monadic value as as argument.
		def __init__(self, mval):
			self.val = mval
		def __repr__(self):
			return self.val.__repr__()

	def FM(basemethod):
		fmapped_basemethod = liftM(basemethod, mreturn, bind)
		def call(*cmargs): # cmargs: not just monadic values, but values wrapped by class_transform
			mval = fmapped_basemethod(*map(lambda x: x.val, cmargs))
			internal_type = type(mval.val)
			return class_transform(name, internal_type, mreturn, bind, fmap)(mval)
		return call

	MethodTransform = DictValueMap(lambda f: FM(f))
	FullClassTransform = DictTransform(MethodRestrictor(), MetaPropertyExcluder(), MethodTransform,
			FunctionalMethodRestrictor())
	newDict = FullClassTransform(basetype.__dict__)
	newtype = type(name, (monad_wrapper,), newDict)
	return newtype



def test():
	# Implementation of the Maybe monad
	class Just(object):
		def __init__(self, i):
			self.val = i
		def __repr__(self):
			return "Just %s" % self.val
	class Nothing(object):
		def __init__(self, *args):
			self.val = None
		def __repr__(self):
			return "Nothing"

	def isJust(x):
		return type(x) == Just
	def allJust(*args):
		return reduce(lambda x, y: x and y, map(lambda x: isJust(x), args))
	def MaybeBind(f, *args):
		# Semantics for multi argument maybe bind: If all arguments are Just, do f. Otherwise, return Nothing.
		if allJust(*args):
			return f(*map(lambda x: x.val, args))
		else:
			return Nothing()
	def MaybeReturn(x):
		return Just(x)
	def MaybeFMap(f):
		returned = lambda *args: MaybeReturn(f(*args))
		return lambda *args: MaybeBind(returned, *args)

	# Normal monadic calls in Python require binds and parens all over the place.
	X = Just(3)
	Y = Just(5)
	print "X + Y in regular monadic values:"
	print MaybeBind(lambda x, y: Just(x + y), X, Y)

	# But with method chaining, the syntax is cleaned up, in that we can use the base methods of the class with the monad instances as if the monadic values were subtypes of their internal types.
	print "Now with method chaining"

	MaybeInt = class_transform("MaybeInt", int, MaybeReturn, bind=MaybeBind)
	A = MaybeInt(Just(3))
	B = MaybeInt(Just(5))
	print A
	print B
	print A + B
	print type(A + B)

	print "works with Nothing"
	A = MaybeInt(Just(3))
	B = MaybeInt(Nothing)
	print A + B
	print type(A + B)

# higher-order abstract syntax
# From TTF.hs in Oleg Kiselyov's lecture notes
def exprTest():

	def Symantics_R():
		class R(object):
			def __init__(self, a):
				self.data = a

		unR = lambda x: x.data

		int_ = lambda i: R(i)

		add = lambda e1, e2: R(unR(e1) + unR(e2))

		lam = lambda f: R(lambda x: unR(f(R(x))))
		app = lambda e1, e2: R(unR(e1)(unR(e2)))

		ev = lambda e: unR(e)

		th1 = add(int_(1), int_(2))
		th2 = lam(lambda x: add(x, x))
		th3 = lam(lambda x: add(app(x, int_(1)), int_(2)))

		print ev(th1)
		print ev(th2)(21)
		print ev(th3)
	Symantics_R()

	def Symantics_S():
		# Python's duck typed as opposed to Haskell, so the specification of S 'looks the same' as R
		class S(object):
			def __init__(self, toString):
				self.toString = toString

		unS = lambda s: s.toString

		# const :: a -> b -> a
		const = lambda x: lambda y: x

		int_ = lambda i: S(const(i.__repr__()))

		add = lambda e1, e2: S(lambda h : "(" + unS(e1)(h) + "+" + unS(e2)(h) + ")")

		# This is really confusing. Reread slowly several times
		def lam(e):
			def arg_to_S(h):
				x = "x" + h.__repr__()
				return "(\\" + x + " -> " + unS(e(S(const(x))))(h + 1) + ")"
			return S(lambda h: arg_to_S(h))
	
		app = lambda e1, e2: S(lambda h: "(" + unS(e1)(h) + " " + unS(e2)(h) + ")")
	
		ev = lambda e: unS(e)(0)

		th1 = add(int_(1), int_(2))
		th2 = lam(lambda x: add(x, x))
		th3 = lam(lambda x: add(app(x, int_(1)), int_(2)))

		print ev(th1)
		print ev(th2)
		print ev(th3)

		# How can we make the syntax cleaner using an applicative functor?

		# What is pure? a -> m a

		pure = int_

		# What is ap? lam: m (a -> b) -> m a -> m b

		ap = lam

		# What is fmap?

		fmap = lambda f: lambda x: pure(ap(f)(x))

		# Then what is the class transform?

		Symantics_S_Int = class_transform("Symantics_S_Int", int, pure, fmap=fmap)

		X = Symantics_S_Int(int_(1))
		Y = Symantics_S_Int(int_(2))
		Z = X + Y

		# Currently error, but this is the rough idea.
		
	Symantics_S()



	
	

if __name__ == "__main__":
	test()
	exprTest();

