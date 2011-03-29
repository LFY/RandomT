from RandomT import *
from RandomT.util import *

def mkZ(x1, x2):
    z = 0
    if x1 > 0 and x2 > 0:
        z = z - 2
    return z

X1 = lambda x1: Gaussian(x1, 0.1)
X2 = lambda x2: Gaussian(x2, 0.1)

# Smoothing around 0:

Expect = lambda V, samples=1000: sum(map(lambda i: sampleVar(V), range(samples))) / float(samples)

MkZ = rfmap(mkZ)

print Expect(MkZ(X1(0), X2(0)))

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import numpy as np

def test1():
    xs = interp_range(-0.5, 0.5, 10)
    ys = interp_range(-0.5, 0.5, 10)

    find = lambda x, y: Expect(MkZ(X1(x), X2(y)))


    fig = plt.figure()
    ax = axes3d.Axes3D(fig)

    X, Y = meshgrid(xs, ys)
    Z = np.array([[find(x, y) for (x, y) in row] for row in coordgrid((X, Y))])

    ax.plot_surface(X, Y, Z)
    plt.show()


# Another example

@rfmap
def Ex2(x0):
    if x0 > 0:
        return x0
    else:
        return 0

def test2():
    xs = interp_range(-0.5, 0.5, 10)
    ys = interp_range(-0.5, 0.5, 10)

    find = lambda x, y: Expect(Ex2(X1(x)))

    fig = plt.figure()
    ax = axes3d.Axes3D(fig)

    X, Y = meshgrid(xs, ys)
    Z = np.array([[find(x, y) for (x, y) in row] for row in coordgrid((X, Y))])

    ax.plot_surface(X, Y, Z)
    plt.show()

test2()
