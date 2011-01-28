def foo():
	print 'hello'
	yield 1
	print 'world'
	yield 2


def foo2(n):
	if (n < 3): yield 1
	else: return
	yield 2

def foo3():
	i = 0
	while 1:
		yield i
		i = i + 1

def pi_series():
	sum = 0
	i = 1.0; j = 1
	while(1):
		sum = sum + j / i
		yield 4 * sum
		i = i + 2; j = j * -1

def firstn(g, n):
	for i in range(n):
		yield g.next()

def euler_accelerator(g):
	s0 = g.next()
	s1 = g.next()
	s2 = g.next()
	sqr = lambda x: x ** 2
	while 1:
		yield s2 - (sqr(s2 - s1)) / (s0 - 2 * s1 + s2)
		s0, s1, s2, = s1, s2, g.next()

def apply_generator(a, b):
	return a(b)

def intsfrom(i):
	while 1:
		yield i
		i = i + 1
	
def exclude_multiples(n, ints):
	for i in ints:
		if (i % n):
			yield i

def sieve(ints):
	while 1:
		prime = ints.next()
		yield prime
		ints = exclude_multiples(prime, ints)

def abc():
	a = deff()
	for i in a:
		yield i
	yield 'abc'

def deff():
	a = ijk()
	for i in a:
		yield i
	yield 'deff'

def ijk():
	for i in (1, 2, 3):
		yield i
	yield 'ijk'

class node(object):
	def __init__(self, dat):
		self.dat = dat
		self.left = 0
		self.right = 0

def inorder(t):
	if t:
		for x in inorder(t.left):
			yield 'left'
			yield x
		yield 'middle'
		yield t.dat
		for x in inorder(t.right):
			yield 'right'
			yield x

def trace(source):
	for item in source:
		print item
		yield item

def to_generator(func):
	def call(*args, **kwargs):
		yield func(*args, **kwargs)
	return call
