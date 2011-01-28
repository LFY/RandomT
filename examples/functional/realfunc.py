from funcclass import Function

def inorder(v):
	if v:
		for u in inorder(v.args[0]):
			yield u
		
		yield v

		for u in inorder(v.args[1]):
			yield u

def preorder(v):
	stack = [v]
	result = []
	visited = {}

	while len(stack) != 0:
		current = stack.pop()
		valid_args = [a for a in current.args if a is not None]
		stack.extend(valid_args)
		result.append(current)

	return result
	
def eval_large(v, *args):
	stack = preorder(v)
	current = []
	values = []
	while len(stack) > 0:
		while len(stack) > 0 and stack[-1].opname == None:
			current.append(stack.pop())
		new_values = map(lambda x: x._simple_call_(*args), current)
		values = new_values + values
		if len(stack) > 0:
			op = stack[-1].opname
			if op == '__add__':
				values.append(values.pop() + values.pop())
			elif op == '__sub__':
				values.append(values.pop() - values.pop())
			elif op == '__rmul__' or op == '__mul__':
				values.append(values.pop() * stack[-1].scalar)
			elif op == '__div__':
				values.append(values.pop() / stack[-1].scalar)
			elif op == 'dot':
				values.append(values.pop() * values.pop())
			else:
				assert(False)
			stack.pop()
			current = []
	return values[0]

	

# Analytic style. No numerical approximations.
class RealFunction(Function):
	def __init__(self, func, la=None, ra=None, name=None, scalar=1):
		Function.__init__(self, func)
		self.args = (la, ra)
		self.opname = name
		self.scalar = scalar
	def __add__(self, other):
		return RealFunction(lambda *x: self.func(*x) + other.func(*x), self, other, '__add__')
	def __sub__(self, other):
		return RealFunction(lambda *x: self.func(*x) - other.func(*x), self, other, '__sub__')		
	def __div__(self, other):
		return RealFunction(lambda *x: self.func(*x) / other, self, None, '__div__', other)
	# Scalar multiplication only for now.
	def __rmul__(self, other):
		return RealFunction(lambda *x: self.func(*x) * other, self, None, '__rmul__', other)
	def __mul__(self, other):
		assert(type(other) is not RealFunction)
		return RealFunction(lambda *x: self.func(*x) * other, self, None, '__mul__', other)
	# Pointwise product.
	def dot(self, other):
		return RealFunction(lambda *x: self.func(*x) * other.func(*x), self, other, 'dot')
	def get_op_seq(self):
		iterator = inorder(self)
		res = []
		for i in iterator:
			res.append(i)
		return res
	
	def _simple_call_(self, *args):
		return self.func(*args)

	def __call__(self, *args):
		return self.func(*args)
#		return eval_large(self, *args)
		
	def getargs(self):
		return self.args
		
def basic_test():
	f = RealFunction(lambda x: x + 1)
	g = RealFunction(lambda x: pow(x, 2))
	
	print f(0)
	print f(1)
	print f(2)
	
	print g(0)
	print g(1)
	print g(2)
	
	h = f + g
	
	print h(1)
	print h(2)
	
	h2 = f.dot(g)

	print h2(2)

from RandomT import *

RandomRealFunction = VectorSpaceRandom(RealFunction, lambda : ZeroFunction(), RealFunction.__add__, RealFunction.__mul__, RealFunction.dot)
	
class ZeroFunction(RealFunction):
	def __init__(self):
		RealFunction.__init__(self, lambda *x: 0, None, None, None)

class IdentityFunction(RealFunction):
	def __init__(self):
		RealFunction.__init__(self, lambda x: x, None, None, None)

from random import randint

# equivalent to f(x) = x + U{0,1}
class AddFlip(RandomRealFunction):
	def __init__(self):
		def draw():
			x = float(randint(0, 1))
			return RealFunction(lambda y: y + x)
		RandomRealFunction.__init__(self, lambda : draw())

def custom_expect(x, samples=50):
	res = ZeroFunction()
	for i in range(samples):
		res += x.sample()
	return res / float(samples)

def custom_var(x, samples=50):
	x2 = x.dot(x)
	exp = custom_expect(x, samples)
	return custom_expect(x2, samples) - exp.dot(exp)
	
RandomRealFunction.expect = custom_expect
RandomRealFunction.var = custom_var

def expect_bug():
	basic_test()

	X = AddFlip()

	EX = X.expect(2)

	print preorder(EX)

	print EX(0)
	print EX(1)
	print EX(2)

	print preorder(EX + EX)
	print (EX + EX)(0)
	print (EX + EX)(1)
	print (EX + EX)(2)

	print (EX + EX)._simple_call_(0)
	print (EX + EX)._simple_call_(1)
	print (EX + EX)._simple_call_(2)

	V = X.var(2)

	print V(0)
	print V(1)
	print V(2)

	print V._simple_call_(0)
	print V._simple_call_(1)
	print V._simple_call_(2)