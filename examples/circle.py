from RandomT import *

from random import uniform
from math import sqrt

Uniform = lambda a, b: RndVar(lambda : uniform(a,b))
X = Uniform(0,1)
Y = Uniform(0,1)
R = rfmap(sqrt)(X * X + Y * Y)
PI = 4 * Pr({R : lambda r: r < 1})

print PI
