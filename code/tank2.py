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

def constArray(val):
    def inner(*args):
        return array(val)
    return inner

# One hour change.
collector = Interval(array) \
    .const([0.1, 60], 60*60) \
    .const([0, 0])

# Five hour delay, then 15 minute draw.
load = Interval(array) \
    .const([0, 0],    60*60*5) \
    .const([0.2, 24], 60*15) \
    .const([0, 0])

N = 20
r = 0.4
h = 1.3
tankModel = tank.model(
    h = h, r = r, N = N,
    P = 5000,
    getAmbient = constArray([24]),
    getLoad = constArray([0.05, 24]),
    getCollector = constArray([0.1, 60])
)

dt = 5
tf = 60 * 60 * 1
x0 = array([45] * N).T
s = simulation.Run(
    xdot = tankModel,
    u = constArray([0]),
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
