import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import simulation
from controllers import mpc
from models import springs, sysTo
from numpy import matrix, hstack, linspace

N = 5
m = 0.1
k = 1
d = 0.1
sys = springs.model(N, m, k, d, 'u', 'obsall')

x0 = matrix([1]*N + [0]*N).T

H = 20
dt = 0.1
controller = mpc.linear(
    H = H,
    dt = dt,
    umax = 3,
    sys = sys
)

tf = 10
s = simulation.Run(
    xdot = sysTo.xdot(sys),
    u = controller,
    x0 = x0,
    dt = dt,
    tf = tf
)
(us, xs) = s.result()
r = hstack(xs)

ts = linspace(0, tf, num = len(r[0,:]))
figure()
try:
    a1 = subplot(211)
    ylabel('Spring extensions')
    for i in range(0, N):
        plot(ts, r[i,:])

    a2 = subplot(212, sharex=a1)
    plot(ts, us)
    ylabel('Control effort')

    savefig('sim.png')
except Exception as e:
    print e
