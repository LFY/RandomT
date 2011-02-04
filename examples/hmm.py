from RandomT import *


# Markov models are special cases of dynamic Bayes networks. We can't express DBNs in their full generality (or at least I don't think so), but this gets pretty close using the fact that a random variable can be captured in a lambda instead of being evaluated outright.

FirstDay = Flip(0.5) # Initializer
NextRain = lambda R: If(R, Flip(0.7), Flip(0.3)) # Transition
Umbrella = lambda R: If(R, Flip(0.9), Flip(0.2)) # "Visible" variable

# What is the probability that it is raining on the first day? (should be 0.5)
print Pr({FirstDay: 1})

# What is the prior probability of using an umbrella on the first day? (should be 0.55)
FirstDayUmbrella = Umbrella(FirstDay)
print Pr({FirstDayUmbrella: 1})
print Pr({FirstDayUmbrella: 1})

# What is the prior probability that it is raining on the second day? (should be 0.5)
SecondDay = NextRain(FirstDay)
print Pr({SecondDay: 1})

# Utility function for multiple application.
def applyN(f, n):
	if n == 1:
		return lambda *a, **aa: f(*a, **aa)
	else:
		return lambda *a, **aa: f(applyN(f, n - 1)(*a, **aa))

# What about the 10th day? (should be 0.5)
# This could really use some optimization....
TenthDay = applyN(NextRain, 10)(FirstDay)

print Pr({TenthDay: 1})

# What is the probability that it rained on the second day given that it rained on the first day?
print Pr({SecondDay: 1}, {FirstDay: 1})

# What is the probability that it rained on the third day given that it rained on the first day?
ThirdDay = NextRain(SecondDay)
print Pr({ThirdDay: 1}, {FirstDay: 1})

# Create a list of random variables Xn where Xi = rains on day i:
L = [FirstDay]
for i in range(5):
	L.append(NextRain(L[-1]))
	
# Take some samples.
print map(lambda x: sampleVar(x), L)
print map(lambda x: sampleVar(x), L)
print map(lambda x: sampleVar(x), L)

# What is the probability that it rains on the 6th day given that it did not rain on the first? (Prediction)
print Pr({L[5] : 1}, {L[0]: 0})

# That it rains the first 4 days?
print Pr({L[0] : 1, L[1]: 1, L[2]: 1, L[3]: 1})

# Create list Un where Ui = umbrella usage on day i:
U = map(lambda x: Umbrella(x), L)

# Takes some samples.
print map(lambda x: sampleVar(x), U)
print map(lambda x: sampleVar(x), U)
print map(lambda x: sampleVar(x), U)
print map(lambda x: sampleVar(x), U)

# What is the probability that I use an umbrella on the first day?
print Pr({U[0] : 1})

# Given that it rains on the first day?
print Pr({U[0]: 1}, {L[0]: 1})

# How about given that it rains on the second day? (Hindsight)
print Pr({U[0]: 1}, {L[1]: 1})

# We've had to use our umbrella every day. What's the probability it was raining for all days? (Most Likely Explanation)
umbrella_evidence = dict(zip(U, [1] * len(U)))

# Pretend this is the most likely explanation. Avenue for future work: Automate finding this query also, without user explicitly implementing likelihood maximization algorithm.
rain_query = dict(zip(L, [1] * len(U)))

print Pr(rain_query, umbrella_evidence)

# Limitations

# Note that this does not work:
SeventhDay = applyN(NextRain, 6)(FirstDay)
FifthDay = applyN(NextRain, 4)(FirstDay)

print Pr({SeventhDay: 1}, {FifthDay: 1})
print Pr({SeventhDay: 1})

# This is because there are two independent computations now. they need to be part of the same computation for inference to work.

# Now consider a list of pairs of (rain, umbrella), defined as a function:

lazy_world = [(FirstDay, Umbrella(FirstDay))]

def extend_model(n):
	if len(lazy_world) < n:
		while(len(lazy_world) < n):
			lazy_world.append((NextRain(lazy_world[-1][0]), Umbrella(NextRain(lazy_world[-1][0]))))

print Pr(lazy_world[0][0], {lazy_world[0][1] : 1})
def RainOnDay(n):
	extend_model(n + 1)
	return lazy_world[n][0]

def UmbrellaOnDay(n):
	extend_model(n + 1)
	return lazy_world[n][1]
	
# Now we can do the queries above without manually unrolling.

print Pr(RainOnDay(0))
print Pr(RainOnDay(0), {UmbrellaOnDay(0) : 1})

print Pr(RainOnDay(3), {UmbrellaOnDay(0) : 1, UmbrellaOnDay(1): 1, UmbrellaOnDay(2): 1, UmbrellaOnDay(2): 1})

print debug_output(Joint(RainOnDay(0), RainOnDay(1), RainOnDay(2)), locals())

print ML(Joint(RainOnDay(0), RainOnDay(1), RainOnDay(2)), {UmbrellaOnDay(0) : 1, UmbrellaOnDay(1): 1, UmbrellaOnDay(2): 1, UmbrellaOnDay(2): 1})

# Consider the particle filter:
def particle_filter(particles, evidence, prior, trans_func, sensor_func):
	trans = trans_func(prior)
	sensor = sensor_func(trans)
	
	new_samples = map(lambda x: sampleVar(trans, {prior : x}), particles)
	weights = normalize(map(lambda x: Pr({sensor: evidence}, {trans: x}), new_samples))
	
	new_distr = {}
	for (k, v) in zip(new_samples, weights):
		new_distr[k] = 0
	for (k, v) in zip(new_samples, weights):
		new_distr[k] += v
	
	new_var = Random(type(new_samples[0]))(Dist(new_distr))
	resample = map(lambda x: sampleVar(new_var), range(len(particles)))
	return resample

def run_obs_sequence(num_particles, observation, prior, trans_func, sensor_func):
	start_particles = map(lambda x: sampleVar(prior), range(num_particles))
	result = [start_particles]
	for evidence in observation:
		result.append(particle_filter(start_particles, evidence, prior, trans_func, sensor_func))
		print "evidence: %s belief: %f particles: %s " % (evidence, float(len(filter(lambda x: x == 1, result[-1]))) / float(len(result[-1])), result[-1])
	return result

# Run on a sequence of observations:
run_obs_sequence(10, [0] * 10 + [1] * 20 + [0] * 5 + [1] * 20, FirstDay, NextRain, Umbrella)



