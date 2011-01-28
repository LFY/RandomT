from scipy import *
from numpy import matrix
from scipy.linalg import inv, det, eig

A = matrix([[1,1,1],[4,4,3],[7,8,5]])
b = matrix([1,2,1]).transpose()

print det(A)
print inv(A) * b
print eig(A)

print "With RandomT:"

from RandomT import *

RandomMatrix = Random(matrix)

A = RandomMatrix([[1,1,1],[4,4,3],[7,8,5]])
print A.sample()

Det = rnd(det)

print Det(A).sample()

Inv = rnd(inv)

# Doesn't work because this numpy.ndarrays are mutable so they are not hashable.
#B = Inv(A)

from scipy.integrate import quad

print quad(lambda x: x**2, 0, 1)

print quad(lambda x: x **3 / (exp(x) - 1), 0.1, 10)

from funcclass import Function

print quad(Function(lambda x: x**2), 0, 1)

Quad = rnd(quad)

from realfunc import RealFunction
from realfunc import AddFlip

addECF("quad")

# A random variable that is the integral of x^2 + x + U{0,1}
X = Quad(AddFlip() + RealFunction(lambda x: x**2), 0, 1)

print debug_output(X[0])
Y = X[0]
print X.sample()
print X.sample()
print X.sample()
print X.sample()
print X.sample()
print X.sample()
print X.sample()

# What is E[X]?
print X[0].expect()

from scipy.integrate import odeint

# odeint: 
# dy/dt
# y @ t_0
# [t_0, t_1]
print odeint(lambda y, t: y, 1, [0, 1])

print odeint(RealFunction(lambda y, t: y), 1, [0, 1])

Odeint = rnd(odeint)

X = Odeint(RealFunction(lambda y, t: y), 1, [0,1])

print X.sample()

import numpy as N

print odeint(lambda y, t: y, 1, N.linspace(0,1,10))

# Doesnt work, unhashable problem again
#X = Odeint(RealFunction(lambda y, t: y), 1, N.linspace(0, 1, 10))

# Cook our own hashable version of linspace
def lspace(a, b, r):
	res = N.linspace(a, b, r)
	res = list(res)
	return res

X = Odeint(RealFunction(lambda y, t: y), Uniform(1, 2), lspace(0, 1, 10))

print X.sample()

# Doesn't work because these are float64's. this is why we need to make expect, var automatically added to the appropriate classes.
# print X[0][0].var()
# The workaround is to use the tolist method to get regular floats in a python list.

# How to print it as a flat Python list instead of a transposed numpy ndarray.
print X.transpose().tolist()[0].sample()

Y = X.transpose().tolist()[0]

for t in lspace(0, 1, 10):
	print t
print
for i in range(5):
	L = Y.sample()
	for y in L:
		print y
	print

print "Variances:"

for i in range(10):
	print Y[i].var(100)


