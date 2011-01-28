# Random class.
from randomt import Random
from randomt import rnd

class Widget(object):
	def __init__(self, a, b):
		self.a = a
		self.b = b
		self.data = a + b
	def foo(self,):
		print self.data
	def getA(self,):
		return self.a
	def getB(self,):
		return self.b
	def __str__(self,):
		return str(self.data)

RandomWidget = Random(Widget)

# New: Can create deterministic RandomWidgets using the base class constructor.
W0 = RandomWidget('abc', '123')

# Keep the old: Can still create RandomWidgets by passing in a lambda.
W1 = RandomWidget(lambda : Widget('abc', '123'))

print W0.sample()
print W0.getA().sample()
print W0.full_info()

print W1.sample()
print W1.getA().sample()
print W1.full_info()

from randomstring import RandomString
from randomstring import Coin

# New: Can create random RandomWidgets using a random version of the base class constructor.
C0 = Coin()
C1 = Coin()

W2 = RandomWidget(C0, C1)
print W2.sample()
print W2.getA().sample()
print W2.full_info()

from randomint import RandomInt

I = RandomInt()
print I.sample()