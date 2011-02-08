from RandomT import *

# colored balls + urn example: this is done in a style where the world is
# viewed as determinsitic with stochastic inputs representing uncertain
# knowledge, not that the urn is inherently stochastic.

# deterministic Urn
class Urn(object):
	def __init__(self, balls):
		self.balls = balls
	def drawNth(self,n):
		return self.balls[:n + 1][-1]

# TODO: make it so that lazynet's rejection sampling properly full-unwraps the deterministic args

N = 5
nRed = 2
nBlue = 3
U = Random(Urn)(lambda : Urn(sampleVar(Permutation(['r'] * nRed + ['b'] * nBlue))))

Draws = map(lambda i: U.drawNth(i), range(N))

print Pr(Draws[1])
print Pr(Draws[1], {Draws[0] : 'r'})
print Pr(Draws[2], {Draws[0] : 'r', Draws[1] : 'r'}) # All possibility of getting another 'r' has been 'drained' from the distribution
print Pr(Draws[3], {Draws[0] : 'r', Draws[1] : 'r', Draws[2] : 'r'})  # This is an impossible situation, so it rightly returns the empty distribution
