import numpy as np
#from scipy import interpolate

# from http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
def interpolate_test():
	x = np.arange(0, 10)
	y = np.exp(-x / 3.0)
	f = interpolate.interp1d(x, y)

	xnew = np.arange(0, 9, 0.1)

	import matplotlib.pyplot as plt

	#plt.plot(x, y, 'o', xnew, f(xnew), '-')
	#plt.show()

	x = np.arange(0, 2 * np.pi + np.pi / 4, 2 * np.pi / 8)
	y = np.sin(x)

	tck = interpolate.splrep(x, y, s=0)
	xnew = np.arange(0, 2 * np.pi, np.pi / 50)
	ynew = interpolate.splev(xnew, tck, der=0)

	def plot_cubic():
		plt.figure()
		plt.plot(x, y, 'x', xnew, ynew, xnew, np.sin(xnew), x, y, 'b')
		plt.legend(['Linear', 'Cubic Spline', 'True'])
		plt.axis([-0.05, 6.33, -1.05, 1.05])
		plt.title('Cubic-spline interpolation')
		plt.show()

	yder = interpolate.splev(xnew, tck, der=1)
	def plot_derivative():
		plt.figure()
		plt.plot(xnew, yder, xnew, np.cos(xnew), '--')
		plt.legend(['Cubic Spline', 'True'])
		plt.axis([-0.05, 5.33, -1.05, 1.05])
		plt.title('Derivative estimation from spline')
		plt.show()

	def integ(x, tck, constant=-1):
		x = np.atleast_1d(x)
		out = np.zeros(x.shape, dtype = x.dtype)
		for n in xrange(len(out)):
			out[n] = interpolate.splint(0, x[n], tck)
		out += constant
		return out
	yint = integ(xnew, tck)
	
	def plot_integral():
		plt.figure()
		plt.plot(xnew, yint, xnew, -np.cos(xnew), '--')
		plt.legend(['Cubic Spline', 'True'])
		plt.axis([-0.05, 6.33, -1.05, 1.05])
		plt.title('Integral estimation from spline')
		plt.show()

	plot_integral()
		
#interpolate_test()

from realfunc import *

class Grid(dict):
	pass


def ptwise_op(a, b, op):
	res = Grid(a)
	for (k, v) in b.items():
		if res.has_key(k):
			res[k] = op(a[k], b[k])
		else:
			res[k] = b[k]
	return res

def add_grid(a, b):
	return ptwise_op(a, b, lambda x, y: x + y)

def mult_grid(a, b):
	return ptwise_op(a, b, lambda x, y: x * y)

def scale_grid(a, s):
	return ptwise_op(a, a, lambda x, y: x * s)


def nearest_pt(g, x):
	k = g.keys()
	l = map(lambda y: abs(y - x), k)
	
	m = min(l)
	
	d = dict(zip(l, k))
	return d[m]	
	
class RealFunctionGrid(object):
	def __init__(self, grid):
		self.grid = grid
	def __add__(self, other):
		return RealFunctionGrid(add_grid(self.grid, other.grid))
	def __sub__(self, other):
		return RealFunctionGrid(add_grid(self.grid, scale_grid(other.grid, -1)))
	def __div__(self, other):
		return RealFunctionGrid(scale_grid(self.grid, 1 / other))
	def __rmul__(self, other):
		return RealFunctionGrid(scale_grid(self.grid, other))
	def __mul__(self, other):
		return RealFunctionGrid(scale_grid(self.grid, other))
	def dot(self, other):
		return RealFunctionGrid(mult_grid(self.grid, other.grid))
	def __call__(self, arg):
		return self.grid[nearest_pt(self.grid, arg)]


def func_to_grid(f, domain):
	return Grid(zip(domain, map(lambda x: f(x), domain)))


def basic_grid_test():
	x = np.arange(0, 10)
	y = np.exp(-x / 3.0)
	g = Grid(zip(x.tolist(), y.tolist()))
	print g
	
	print add_grid(g, g)
	
	print scale_grid(g, 69)
	
	f = func_to_grid(lambda x: x, np.arange(0, 10).tolist())
	print f
	
	from math import sin
	g = func_to_grid(lambda x: sin(x), np.arange(0, 10).tolist())
	
	print g
	
	print add_grid(f, g)
	
	F = RealFunctionGrid(f)
	G = RealFunctionGrid(g)
	
	print F(0)
	print F(1)
	print F(2)
	
	H = F + G
	
	print H(0)
	print H(1)
	print H(2)

def linear_interp(grid, x):
	if grid.has_key(x):
		return x
	else:
		k = grid.keys()
		l = map(lambda y: y - x, k)
		begin = 0
		end = len(l) - 1

		i = 0
		while l[begin + 1] < 0:
			begin = begin + 1
		while l[end - 1] > 0:
			end = end - 1

		return grid[begin] + (grid[end] - grid[begin]) * (x - grid[begin])

class PiecewiseLinear(RealFunctionGrid):
	def __init__(self, grid):
		self.grid = grid
	def __add__(self, other):
		return PiecewiseLinear(add_grid(self.grid, other.grid))
	def __sub__(self, other):
		return PiecewiseLinear(add_grid(self.grid, scale_grid(other.grid, -1)))
	def __div__(self, other):
		return PiecewiseLinear(scale_grid(self.grid, 1 / other))
	def __rmul__(self, other):
		return PiecewiseLinear(scale_grid(self.grid, other))
	def __mul__(self, other):
		return PiecewiseLinear(scale_grid(self.grid, other))
	def dot(self, other):
		return PiecewiseLinear(mult_grid(self.grid, other.grid))
	def __call__(self, arg):
		return linear_interp(self.grid, arg)

def linear_interp_test():
	f = func_to_grid(lambda x: x, np.arange(0, 10).tolist())
	print f
	print linear_interp(f, 0)
	print linear_interp(f, 0.5)
	print linear_interp(f, 1.5)
	print linear_interp(f, 2.5)
	print linear_interp(f, 3.5)

	F = PiecewiseLinear(f)

	print F(0)
	print F(1)
	print F(2)

	
class Spline(RealFunctionGrid):
	def __init__(self, grid):
		self.grid = grid
		pts = grid.items()

		xvals = zip(*pts)[0]
		yvals = zip(*pts)[1]
		self.splrep = interpolate.splrep(xvals, yvals, s=0)
	def __add__(self, other):
		return Spline(add_grid(self.grid, other.grid))
	def __sub__(self, other):
		return Spline(add_grid(self.grid, scale_grid(other.grid, -1)))
	def __div__(self, other):
		return Spline(scale_grid(self.grid, 1 / other))
	def __rmul__(self, other):
		return Spline(scale_grid(self.grid, other))
	def __mul__(self, other):
		return Spline(scale_grid(self.grid, other))
	def dot(self, other):
		return Spline(mult_grid(self.grid, other.grid))
	def __call__(self, arg):
		return interpolate.splev(arg, self.splrep, der=0)

def spline_test():
	f = func_to_grid(lambda x: x ** 2, np.arange(0, 10).tolist())
	print f
	F = Spline(f)
	print F(0)
	print F(1)
	print F(2)
	print F(3)

from RandomT import *

RandomSpline = Random(Spline)

