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

Expect = lambda V, samples=100: reduce(lambda x, y: x + y, map(lambda i: sampleVar(V), range(samples))) / float(samples)

MkZ = rfmap(mkZ)

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

def test3():
    xs = interp_range(-0.5, 0.5, 10)
    ys = interp_range(-0.5, 0.5, 10)

    find = lambda x, y: Expect(MkZ(X1(x), X2(y)))

    xyzs = dict([((x, y), find(x, y)) for x in xs for y in ys])

class Vec(tuple):
    def __add__(self, other):
        return Vec(tuple(map(lambda (x, y): x + y, zip(self, other))))
    def __rdiv__(self, d):
        return Vec(tuple(map(lambda x: x / d, self)))
    def __div__(self, d):
        return Vec(tuple(map(lambda x: x / d, self)))

def test4(): 
    p = [5, 15, 25, 40, 60]
    alpha = lambda i, v: 1.0 / (1 + (v - p[i - 1])**2/25.0)
    T = 20
    dt = 0.1
    drag = 0.0005

    def gearbox(s1, s2, s3, s4):
        t, v, gear, nxt, w = 0,0,1,1,0.8
       
        res = []

        while (t < T):
            res += [v]
            if gear > 0:
                v = v + dt * (v * alpha(gear , v) + 5.0)
            else:
                v = v - dt * (v * v * drag)

            if gear == 1 and v > s1:
                gear = 0; nxt = 2; w = 0.8;
            if gear == 2 and v > s2:
                gear = 0; nxt = 3; w = 0.8;
            if gear == 3 and v > s3:
                gear = 0; nxt = 4; w = 0.8;
            if gear == 4 and v > s4:
                gear = 0; nxt = 5; w = 0.8;

            if w < 0.0 and gear == 0:
                gear = nxt

            t += dt
            w -= dt

        return Vec(tuple(res))

    target = gearbox(14, 24, 40, 65)

    from math import sqrt

    Error = rfmap(lambda res: sqrt(sum(map(lambda (r, t): (r - t)**2, zip(res, target)))))

    xs = interp_range(0, 80, 100)

    def plot_smoothed(var, samples=100):
        Geartest1 = rfmap(lambda s1: gearbox(s1, 24, 40, 65))
        find1 = lambda x: Expect(Error(Geartest1(Gaussian(x, var))), samples)
        plt.plot(xs, map(find1, xs))
        
        Geartest2 = rfmap(lambda s2: gearbox(14, s2, 40, 65))
        find2 = lambda x: Expect(Error(Geartest2(Gaussian(x, var))), samples)
        plt.plot(xs, map(find2, xs))

        Geartest3 = rfmap(lambda s3: gearbox(14, 24, s3, 65))
        find3 = lambda x: Expect(Error(Geartest3(Gaussian(x, var))), samples)
        plt.plot(xs, map(find3, xs))

        Geartest4 = rfmap(lambda s4: gearbox(14, 24, 40, s4))
        find4 = lambda x: Expect(Error(Geartest4(Gaussian(x, var))), samples)
        plt.plot(xs, map(find4, xs))

    plot_smoothed(0.0, 1)
    plot_smoothed(2.0, 1000)

    plt.savefig('gearbox.pdf')




