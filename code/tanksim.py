import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import simulation
from controllers import mpc
from models import tank
from numpy import matrix, hstack, vstack, linspace, zeros, ones
from operator import mul

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

def constMat(val):
    def inner(*args):
        return matrix([[val]])
    return inner

N = 20
r = 0.4
h = 1.3
tankModel = tank.model(
    h = h, r = r, N = N,
    getAmbient = constMat(20),
    getLoad = constMat(0)
)

dt = 0.1
tf = 20
x0 = matrix(range(N)).T
s = simulation.Run(
    xdot = tankModel,
    x0 = x0,
    dt = dt,
    tf = tf
)

(us, xs) = s.result()
ts = linspace(0, tf, num = len(xs[0,:]))

try:
    figure()
    a1 = subplot(211)
    ylabel('Tank temperatures')
    for i in range(0, N):
        plot(ts, xs[i,:])

    a2 = subplot(212, sharex=a1)
    for i in range(len(us[:,0])):
        step(ts, us[i,:])
    ylabel('Control effort')

    axis(map(mul, [1, 1, 1.1, 1.1], axis()))
    savefig('sim.png')

except Exception as e:
    print e
