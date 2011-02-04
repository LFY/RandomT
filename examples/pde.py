# On characterizing the uncertainty of the
# analytical solution to the one-dimensional no diffusion advection PDE.

v = 1.0

# As an example pulse function: the sine wave.
from math import sin

# the analytical solution here is that the amplitude of the wave at some t is
# u_t = initial(x - v t)
def advect(f, x, t):
	return f(x - v * t)

print "Analytical solution to advection equation in 1D for u_0(x, t) = sin(x):"

print "u(x, t): x = 0 t = 0: %f" % advect(sin, 0, 0)
print "u(x, t): x = 0 t = 1: %f" % advect(sin, 0, 1)

def u(x, t):
	return advect(sin, x, t)

print "u(x, t): x = 0 t = 5: %f" % u(0, 5)
print "u(x, t): x = 0 t = 10: %f" % u(0, 10)

# Uncertainty in initial conditions.

# This can be any function from an arbitrary random number library. We're using uniform here.
from random import uniform

# introducing the randomly perturbed sine wave: a sine wave with a uniformly distributed random number added to it.
def random_sin(x):
	return sin(x) + uniform(-0.2, 0.2)

# Now we redefine u(x, t) to take the random sine as the initial condition.
def u(x, t):
	return advect(random_sin, x, t)

print "Analytical solution to advection equation where initial condition is uncertain by an additive uniform random variate:"

print "u(x, t): x = 0 t = 0: %f"  % u(0, 0)
print "u(x, t): x = 0 t = 1: %f"  % u(0, 1)
print "u(x, t): x = 0 t = 5: %f"  % u(0, 5)
print "u(x, t): x = 0 t = 10: %f"  % u(0, 10)

# How do we do uncertainty quantification on u(x, t)?

# Let's start with a few simple questions:

# 1. What is the expected value of u(x, t) over time?
# 2. What is its variance?

# Our probabilistic programming language
from RandomT import *

# rnd: Transforms a function to output a formal random variable and take formal random variables as inputs.
U = rnd(u)

# Now we have created a random variable whose distribution is characterized by
# u(x, t) with the uncertain initial conditions.

print "Draws from the random variable U = u(x, t) with uncertain initial conditions."
print "draw from U @ x = 0 t = 0: %f" % sampleVar(U(0, 0))
print "draw from U @ x = 0 t = 0: %f" % sampleVar(U(0, 0))
print "draw from U @ x = 0 t = 0: %f" % sampleVar(U(0, 0))

print "E[U @ x = 0, t = 0]: %f" % U(0, 0).expect()
print "Var[U @ x = 0, t = 0]: %f" % U(0, 0).var()
print "Var[U @ x = 0, t = 1]: %f" % U(0, 1).var()
print "Var[U @ x = 0, t = 5]: %f" % U(0, 5).var()
print "Var[U @ x = 0, t = 10]: %f" % U(0, 10).var()

# What about characterizing uncertainty in velocity?

# Create a new function parameterized by velocity:
def u(x, t, v):
	return sin(x - v * t)

# Create the random variable as before.
U = rnd(u)

# This Uniform represents a formal random variable whose distribution is uniform, as opposed to the "uniform" used above, which is just a plain function that returns floating point numbers unreliably.
from RandomT import Uniform

print "Analytical solution to advection equation where velocity is uncertain by a uniform random variate:"
print "Let U = u(x,t) under this uncertainty."
print "draw from U @ x = 0, t = 0: %f" % sampleVar(U(0, 0, Uniform(1, 2)))
print "draw from U @ x = 0, t = 1: %f" % sampleVar(U(0, 1, Uniform(1, 2)))

print "E[U @ x = 0, t = 0]: %f" % U(0, 0, Uniform(1, 2)).expect()
print "Var[U @ x = 0, t = 0]: %f" % U(0, 0, Uniform(1, 2)).var()
print "Var[U @ x = 0, t = 1]: %f" % U(0, 1, Uniform(1, 2)).var()
print "Var[U @ x = 0, t = 5]: %f" % U(0, 5, Uniform(1, 2)).var()
print "Var[U @ x = 0, t = 10]: %f" % U(0, 10, Uniform(1, 2)).var()

print "We see that the variance generally increases over time because it is uncertainty in velocity."

