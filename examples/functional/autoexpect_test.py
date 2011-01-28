from RandomT import *


# Decimals

from decimal import Decimal

def scalar_mult(x, floaty):
	return x * Decimal(str(floaty))

RandomDecimal = VectorSpaceRandom(Decimal, lambda : Decimal(), Decimal.__add__, scalar_mult, Decimal.__mul__)

X = RandomDecimal('1.0')

print X.expect()
print X.var()

class Vector3D(object):
	def __init__(self, x=0, y=0, z=0):
		self.x = x
		self.y = y
		self.z = z
	def __add__(self, other):
		return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
	def __sub__(self, other):
		return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
	def __mul__(self, s):
		return Vector3D(self.x * s, self.y * s, self.z * s)
	def __rmul__(self, s):
		return self.__mul__(s)
	def __str__(self):
		return "%f %f %f" % (self.x, self.y, self.z)


class Matrix3D(object):
	def __init__(self, data=[[0] * 3] * 3):
		self.data = data
	def __add__(self, other):
		newdata = [[x + y for (x, y) in zip(u, v)] for (u, v) in zip(self.data, other.data)]
		return Matrix3D(newdata)
	def __sub__(self, other):
		newdata = [[x - y for (x, y) in zip(u, v)] for (u, v) in zip(self.data, other.data)]
		return Matrix3D(newdata)		
	def __mul__(self, s):
		newdata = [[x * s for x in u] for u in self.data]
		return Matrix3D(newdata)
	def __rmul__(self, s):
		return self.__mul__(s)
	def __str__(self):
		return str(self.data)
		
def outer(u, v):
	return Matrix3D([[u.x * v.x, u.x * v.y, u.x * v.z], [u.y * v.x, u.y * v.y, u.y * v.z], [u.z * v.x, u.z * v.y, u.z * v.z]])
		
RandomVector3D = VectorSpaceRandom(Vector3D, lambda : Vector3D(),  Vector3D.__add__, Vector3D.__mul__, outer)
RandomMatrix3D = VectorSpaceRandom(Matrix3D, lambda : Matrix3D(), Matrix3D.__add__, Matrix3D.__mul__)

X = RandomVector3D(0, 0, 0)

print X.sample()
print X.expect()

print Matrix3D()

x = X.sample()

print outer(x, x)

print X.var()

from random import gauss

class Gauss3D(RandomVector3D):
	def __init__(self, means, var):
		self.means = means
		self.vars = var
		def draw():
			x = gauss(means[0], var[0])
			y = gauss(means[1], var[1])
			z = gauss(means[2], var[2])
			return Vector3D(x, y, z)
		RandomVector3D.__init__(self, lambda : draw())
	def expect(self, samples=9001):
		return Vector3D(self.means[0], self.means[1], self.means[2])
	
		

X = Gauss3D([0, 0, 0], [1, 1, 1])

print X.sample()

print X.expect()

print X.var()

print Expectation(X)