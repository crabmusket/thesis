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
d = 0.01
springSys = springs.model(N, m, k, d, 'u', 'obsall')

x0 = matrix([1, 0]*N).transpose()

H = 20
dt = 0.1
controller = mpc.law(
    H = H,
    dt = dt,
    umax = 3,
    sys = springSys
)

tf = 30

s = simulation.Run(
    xdot = sysTo.xdot(springSys),
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
    hold(True)
    for i in [0]:#range(0, N):
        plot(ts, r[2*i,:])
    plot(ts, us)
    savefig('sim.png')
    hold(False)
except Exception as e:
    print e
