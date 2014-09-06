print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import simulation
from simulation.interval import Interval
from controllers import mpc
from models import tank2 as tank
from numpy import array, linspace
from operator import add

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)
print 'Beginning simulation'

# Charges at hour 0 and hour 6.
collector = Interval(array) \
    .const([0.1, 60], 60*60) \
    .const([0, 0], 60*60*5) \
    .const([0.05, 60], 60*60*2) \
    .const([0, 0])

# 15 minute draw at hour 4.
load = Interval(array) \
    .const([0, 0],    60*60*4) \
    .const([0.2, 24], 60*15) \
    .const([0, 0])

N = 20
r = 0.4
h = 1.3
tankModel = tank.model(
    h = h, r = r, N = N,
    P = 1000,
    auxOutlet = N/2,
    getAmbient = Interval(array).const([24]),
    getLoad = Interval(array).const([0, 24]),
    getCollector = Interval(array).const([0, 60])
)

dt = 5
tf = 60 * 60 * 3
x0 = array([45] * N).T
s = simulation.Run(
    xdot = tankModel,
    u = lambda *args: array([0.01]),
    x0 = x0,
    dt = dt,
    tf = tf
)

(us, xs) = s.result()
ts = linspace(0, tf, num = len(xs[0,:]))

toHours = lambda ts: map(lambda t: t / (60*60), ts)

try:
    figure()
    #a1 = subplot(211)
    ylabel('Tank temperatures')
    xlabel('Time (h)')
    hs = [plot(toHours(ts), xs[i,:])[0] for i in range(N)]
    ls = [str(i) for i in range(N)]
    legend(reversed(hs), reversed(ls), fontsize=10)

    #a2 = subplot(212, sharex=a1)
    #for i in range(len(us[:,0])):
    #    step(ts, us[i,:])
    #ylabel('Control effort')
    #xlabel('Time (s)')

    axis(map(add, [0, 0, -2, 2], axis()))
    savefig('sim.png')

except Exception as e:
    print e
