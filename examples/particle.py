from RandomT import *

FirstDay = Flip(0.5) # Initializer
NextRain = lambda R: If(R, Flip(0.7), Flip(0.3)) # Transition
Umbrella = lambda R: If(R, Flip(0.9), Flip(0.2)) # "Visible" variable

lazy_world = [(FirstDay, Umbrella(FirstDay))]

def extend_model(n):
	if len(lazy_world) < n:
		while(len(lazy_world) < n):
			lazy_world.append((NextRain(lazy_world[-1][0]), Umbrella(NextRain(lazy_world[-1][0]))))

def RainOnDay(n):
	extend_model(n + 1)
	return lazy_world[n][0]

def UmbrellaOnDay(n):
	extend_model(n + 1)
	return lazy_world[n][1]
	
def particle_filter(particles, evidence, prior, trans_func, sensor_func):
	trans = trans_func(prior)
	sensor = sensor_func(trans)
	
	new_samples = map(lambda x: sampleVar(trans, {prior : x}), particles)
	weights = normalize(map(lambda x: PrN({sensor: evidence}, {trans: x})(100), new_samples))
	
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



