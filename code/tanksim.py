print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import simulation
from controllers import mpc
from models import tank
from numpy import array, linspace
from operator import mul

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)
print 'Beginning simulation'

def constArray(val):
    def inner(*args):
        return array(val)
    return inner

N = 20
r = 0.4
h = 1.3
tankModel = tank.model(
    h = h, r = r, N = N,
    heat = [],
    P = 000,
    getAmbient = constArray([24]),
    getLoad = constArray([0])
)

dt = 1
tf = 100
x0 = array([45] * N).T
s = simulation.Run(
    xdot = tankModel,
    u = constArray([1]),
    x0 = x0,
    dt = dt,
    tf = tf
)

(us, xs) = s.result()
ts = linspace(0, tf, num = len(xs[0,:]))

try:
    figure()
    #a1 = subplot(211)
    ylabel('Tank temperatures')
    xlabel('Time (s)')
    hs = [plot(ts, xs[i,:])[0] for i in range(N)]
    legend(hs, map(str, range(N)), fontsize=10)

    #a2 = subplot(212, sharex=a1)
    #for i in range(len(us[:,0])):
    #    step(ts, us[i,:])
    #ylabel('Control effort')
    #xlabel('Time (s)')

    #axis(map(mul, [1, 1, 1.1, 1.1], axis()))
    savefig('sim.png')

except Exception as e:
    print e
