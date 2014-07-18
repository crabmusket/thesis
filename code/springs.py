import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import simulation
from controllers import mpc
from models import springs, sysTo
from numpy import matrix, hstack, vstack, linspace, zeros, ones

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

N = 5
m = 0.1
k = 1
d = 0.1
sys = springs.model(N, m, k, d,
    control = [N],
    disturb = [2*N-1],
    observe = 'all'
)

def stepFn(ts, before, after):
    def inner(t, *args):
        if t < ts:
            return before
        else:
            return after
    return inner
dist = stepFn(10, matrix([[0]]), matrix([[1]]))

H = 20
dt = 0.1
controller = mpc.linear(H, dt,
    sys = sys,
    umax = 3
)

tf = 20
x0 = matrix([1]*N + [0]*N).T
s = simulation.Run(
    xdot = sysTo.xdot(sys, None),
    u = controller,
    x0 = x0,
    dt = dt,
    tf = tf
)

(us, xs) = s.result()
ts = linspace(0, tf, num = len(xs[0,:]))

try:
    figure()
    a1 = subplot(211)
    ylabel('Mass positions')
    for i in range(0, N):#[N-1, 0]:
        plot(ts, xs[i,:])

    a2 = subplot(212, sharex=a1)
    for i in range(len(us[:,0])):
        step(ts, us[i,:])
    ylabel('Control effort')

    savefig('sim.png')

except Exception as e:
    print e
