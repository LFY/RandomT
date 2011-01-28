# Now consider a numerical solution:

# class for wave pulses. 
class Pulse(object):
	def __init__(self, data):
		self.res = len(data)
		self.data = data
	def size(self):
		return self.res
	def getData(self):
		return self.data
	def __getitem__(self, i):
		real_index = i % self.res
		return self.data[real_index]
	def __str__(self,):
		res = ""
		for d in self.data:
			res += "%f\t" % (d)
		return res

def advect_timestep(pulse, integrator, v, dx, dt):
	new_data = []
	for i in range(pulse.size()):
		new_data.append(integrator(pulse, v, dx, dt, i))
	return Pulse(new_data)
	
# FTCS
def FTCS(pulse, v, dx, dt, i):
	return pulse[i] - dt * v / dx * 0.5 * (pulse[i + 1] - pulse[i - 1])
	
# Lax
def Lax(pulse, v, dx, dt, i):
	return 0.5 * (pulse[i + 1] + pulse[i - 1]) - v * dt / dx * 0.5 * (pulse[i + 1] - pulse[i - 1])
	
# Lax-Wendroff
def Lax_Wendroff(pulse, v, dx, dt, i):
	return pulse[i] - v * dt / dx * 0.5 * (pulse[i + 1] - pulse[i - 1]) + 0.5 * pow(v * dt / dx, 2) * (pulse[i + 1] - 2 * pulse[i] + pulse[i - 1])

test_data = [0.0, 0.0, 1.0, 0.0]

P = Pulse(test_data)

from math import exp
from math import pi

def gauss_pdf(x):
	mean = 0
	var = 1
	return pow(2 * pi * var, -0.5) * exp(-(x - mean) * (x - mean) / (2.0 * var))

def generate_pulse(resolution, size, pulse_func):
	t = lambda x: (x - 0.5 * resolution) / resolution * size
	return [pulse_func(t(x)) for x in range(resolution)]
	
P = Pulse(generate_pulse(100, 4, gauss_pdf))

def wave_at(initial, x, tf):
	v = 1.0
	dt = 0.1
	dx = 0.1
	integrator = Lax_Wendroff
	
	t = 0

	cur_pulse = initial
	while t < tf:
		cur_pulse = advect_timestep(cur_pulse, integrator, v, dx, dt)
		t += dt
	return cur_pulse

#for i in range(5):
#	print wave_at(P, 0.5, 3 * i)

from RandomT import *

# Encoding the boundary conditions.

# FTCS
def FTCS(pulse, v, dx, dt, i):
	prev = i - 1
	next = i + 1
	if i == len(pulse) - 1:
		next = 0
	if i == 0:
		prev = len(pulse) - 1
		
	return pulse[i] - dt * v / dx * 0.5 * (pulse[next] - pulse[prev])
	
# Lax
def Lax(pulse, v, dx, dt, i):
	prev = i - 1
	next = i + 1
	if i == len(pulse) - 1:
		next = 0
	if i == 0:
		prev = len(pulse) - 1
		
	return 0.5 * (pulse[next] + pulse[prev]) - v * dt / dx * 0.5 * (pulse[next] - pulse[prev])
	
# Lax-Wendroff
def Lax_Wendroff(pulse, v, dx, dt, i):
	prev = i - 1
	next = i + 1
	if i == len(pulse) - 1:
		next = 0
	if i == 0:
		prev = len(pulse) - 1
		
	return pulse[i] - v * dt / dx * 0.5 * (pulse[next] - pulse[prev]) + 0.5 * pow(v * dt / dx, 2) * (pulse[next] - 2 * pulse[i] + pulse[prev])
	
	
# Generic way of shifting a pulse by a (consistent) uniform variate.
def generate_uncertain_pulse(resolution, size, pulse_func, delta=0.2):
	U = Uniform(-delta, delta)
	l = generate_pulse(resolution, size, pulse_func)
	return [x + U for x in l]

# Specific way of doing so:
U = Uniform(-0.2, 0.2)

# Establish a baseline variance:
print "Variance of U[-0.2, 0.2]: %f" % U.var()

L = generate_pulse(4, 4, lambda x: 0.0)

# Generate the joint distribution.
R = [x + U for x in L]

# A check for consistency, that in fact the values here are being shifted by the same consistent uniform random variable:

print "Consistency check: Pr(R[0] > 1 | R[1] > 1): should be 1.0"
print Pr({R[0]: lambda x: x > 0.1}, {R[1]: lambda x: x > 0.1})

# Otherwise the probability wouldn't be 1.

# Now we might ask about the uncertainty of FTCS, Lax, and Lax-Wendroff, at each point in the domain after one step:

def evaluate_variance(R):
	v = 1.0
	dx = 0.1
	dt = 0.1
	
	for i in range(len(R)):
		print "Var[Input] at %d: %f" % (i, R[i].var())
		print "Var[FTCS] at %d: %f" % (i, FTCS(R, v, dx, dt, i).var())
		print "Var[Lax] at %d: %f" % (i, Lax(R, v, dx, dt, i).var())
		print "Var[Lax_Wendroff] at %d: %f" % (i, Lax_Wendroff(R, v, dx, dt, i).var())

print "Variance for a constant initial condition:"
#evaluate_variance(R)

# Now what if we want to analyze an uncertain gaussian pulse?
L = generate_pulse(4, 4, gauss_pdf)
R = [x + U for x in L]

print "Variance for a gaussian initial condition:"
#evaluate_variance(R)

def advect_timestep(pulse, integrator, v, dx, dt):
	new_data = []
	for i in range(len(pulse)):
		new_data.append(integrator(pulse, v, dx, dt, i))
	return new_data

def wave_at(initial, x, tf, integrator=FTCS):
	v = 1.0
	dt = 0.1
	dx = 0.1
	t = 0
	
	cur_pulse = initial
	while t < tf:
		cur_pulse = advect_timestep(cur_pulse, integrator, v, dx, dt)
		t += dt
	return cur_pulse

def evaluate_variance(R, x, t, integrator=FTCS):
	print [x.var() for x in wave_at(R, x, t, integrator)]

L = generate_pulse(4, 4, gauss_pdf)
R = [x + U for x in L]
	
#evaluate_variance(R, 0, 1, FTCS)

# A faster way of writing it:

# Need to ignore or promote function arguments so we dont need to curry it away here.
MyIntegrator = Lax_Wendroff

Wave_At = rnd(lambda i, x, t: wave_at(i, x, t, MyIntegrator))

R2 = R
from random import uniform

def offset_pulse(l, delta=0.2):
	o = uniform(-delta, delta)
	return [x + o for x in l]

R = RandomList(lambda : offset_pulse(generate_pulse(4, 4, gauss_pdf)))

# And how to deal with RandomLists full of RandomInts.
def evaluate_variance(R, x, t):
	S = Wave_At(R, x, t)
	
	l = len(S.sample())
	
	Result = []
	for i in range(l):
		Result.append(RandomFloat(lambda : S[i].sample()))
	
	return [x.var() for x in Result]

def toRandomFloats(l):
	res = []
	for i in range(len(l.sample())):
		res.append(RandomFloat(lambda: l[i].sample()))
	return res

print "Variance of input: %s" % [x.var() for x in toRandomFloats(R)]
print "Variance at x = 0 t = 0.1: %s" % evaluate_variance(R, 0, 0.1)	
print "Variance at x = 0 t = 1.0: %s" % evaluate_variance(R, 0, 1)	
print "Variance at x = 0 t = 5.0: %s" % evaluate_variance(R, 0, 5)	

