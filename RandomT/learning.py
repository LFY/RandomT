from randomt import Random
from randomt import rnd

from cpt import normalize
from probrep import Dist

def weighted_histogram_dist(samples, weights):
	weights = normalize(weights)
	new_distr = {}
	for (k, v) in zip(samples, weights):
		new_distr[k] = 0
	for (k, v) in zip(samples, weights):
		new_distr[k] += v
		
	result_type = type(samples[0])
	return Random(result_type)(Dist(new_distr))
	
def histogram_dist(data):
	return weighted_histogram_dist(data, len(data) * [1.0])

# data: a tuple of type T
# returns a Random[T] with distribution according to data
def learn_variable(data, learn_alg=histogram_dist):
	return learn_alg(data)

def learn_from_sampling_function(func, samples=2000):
	l = [func() for x in range(samples)]
	return histogram_dist(l)

def particle_filter(particles, evidence, prior, trans_func, sensor_func):
	trans = trans_func(prior)
	sensor = sensor_func(trans)
	
	new_samples = map(lambda x: trans.sample({prior : x}), particles)
	weights = normalize(map(lambda x: Pr({sensor: evidence}, {trans: x}), new_samples))

	new_var = weighted_histogram_dist(new_samples, weights)

	return new_var

