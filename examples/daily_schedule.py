from RandomT import *

# Based on the similar example in HANSEI
# Currently cannot quite express the predicate only_on, so can't yet deal with activites on multiple days

# predicate: extensional equality
@rnd
def Eq(a, b):
	return a == b
@rnd
def Disjoint(xs, ys):
	return len(set(xs).intersect(set(ys))) == 0

def schedule_model():
	# For the daily schedule for Monday to Wednesday:
	ndays = 3

	# One of the days I'll shop.
	shopday = UniformInt(range(ndays))

	# One of the days I'll take a walk.
	walkday = UniformInt(range(ndays))

	# One of the days I'll go to the barber.
	barberday = UniformInt(range(ndays))

	# One of the days I'll go to the supermarket.
	superday = UniformInt(range(ndays))

	# The same day as I go to the supermarket, I'll shop.
	super_shop_pred = Eq(shopday, superday)

	# The same day as I talk a walk I'll go to the barber.
	walk_barber_pred = Eq(walkday, barberday)

	# I'll go to the supermarket the day before the day I'll take a walk.
	super_walk_pred = Eq(superday, walkday - 1)

	# I'll take a walk Tuesday.
	tues_walk_pred = Eq(1, walkday)

	all_acts = Joint(shopday, walkday, barberday, superday)

	# Conditioning statement = evidence
	# evidence of all predicates holding = specify consistent worlds
	consistent = {super_shop_pred: True, walk_barber_pred: True, super_walk_pred: True, tues_walk_pred:True}

	# 1000 samples usually enough to get the answer
	print Pr(Joint(shopday, walkday, barberday, superday), consistent, lambda model : RejectionSampler(model, 1000))
	# Using BNT for exact inference: Messy output, so just return what's in the support
	#print dict(filter(lambda (k, v): v > 0.0, Pr(Joint(shopday, walkday, barberday, superday), consistent, BNTEngine).items()))

schedule_model()
