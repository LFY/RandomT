# Random[T] take on Microsoft's (improperly coded) permutation function.
# more at http://www.robweir.com/blog/2010/02/microsoft-random-browser-ballot.html

from RandomT import *

# The browsers over which we want to create a random permutation.
browsers = ["IE", "Firefox", "Opera", "Chrome", "Safari"]

# Python port of how Microsoft did it: a comparator function that returns a random number.
def ms_permutation(l):
	return sorted(l, lambda x, y: UniformInt([-1, 1]).sample())

# 50 random (but not uniformly random) permutations:
for i in range(50):
	print ms_permutation(browsers)

# Just looking at ms_permutation, we see that it could be biased based on how the sort function works. Is it biased? Let's create a random variable to find out.
B = RandomTuple(lambda : tuple(ms_permutation(browsers)))

# If it is not biased, IE should have the same chance of occuring in any of the 5 positions.
print B.index('IE').get_distr() # Oh no, it doesn't.

# Let's use Random[T]'s Permutation class which in turn uses Python's built-in shuffle function.
B = Permutation(browsers)

# This looks less biased.
print "Python's built-in shuffle:"
print B.index('IE').get_distr()

# What about for the other browsers?
print B.index('Firefox').get_distr()
print B.index('Opera').get_distr()
print B.index('Chrome').get_distr()
print B.index('Safari').get_distr()

# So it's not just that we can correctly specify random permutations, it's that we can check the biasedness of a variable in a concise manner. 

# Fisher-Yates shuffle:
from random import randint
def fy_shuffle(l):
	m = len(l)
	a = range(m)
	a[0] = l[0]
	for i in range(m)[1:]:
		j = randint(0, i)
		a[i] = a[j]
		a[j] = l[i]
	return a

# Is it biased?
B = RandomTuple(lambda : tuple(fy_shuffle(browsers)))

print "Explicitly implementing Fisher-Yates shuffle:"
print B.index('IE').get_distr()