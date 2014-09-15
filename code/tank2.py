print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

import simulation
from simulation.interval import Interval
from controllers.thermostat import thermostat
from models import tank2 as tank
from numpy import array, linspace
from operator import add
from datetime import timedelta, datetime
import prediction.ambient
import prediction.load

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

startTime = datetime(2014, 9, 9, 04, 00, 00)
ambient = prediction.ambient.make(start = startTime)
load = prediction.load.make(start = startTime, mainsTemp = ambient)

N = 20
r = 0.4
h = 1.3
auxOutlet = N/2
tankModel = tank.model(
    h = h, r = r, N = N,
    P = 2000,
    auxOutlet = auxOutlet,
    getAmbient = ambient,
    getLoad = load,
    getCollector = Interval(array).const([0, 60])
)

dt = 30
tf = 60 * 60 * 24
x0 = array([24] * N).T
s = simulation.Run(
    xdot = tankModel,
    u = thermostat(auxOutlet, 0.03, 60, 5),
    x0 = x0,
    dt = dt,
    tf = tf
)

(us, xs) = s.result()
ts = linspace(0, tf, num = len(xs[0,:]))

toHours = lambda ts: map(lambda t: t / (60*60), ts)
th = toHours(ts)

try:
    figure()
    a1 = subplot(311)
    ylabel('Tank temperatures')
    xlabel('Time (h)')
    hs = [plot(th, xs[i,:])[0] for i in range(N)]
    ls = [str(i) for i in range(N)]
    axis(map(add, [0, 0, -1, 1], axis()))

    a2 = subplot(312, sharex=a1)
    for i in range(len(us[:,0])):
        step(th, us[i,:])
    ylabel('Control effort')
    xlabel('Time (h)')
    axis(map(add, [0, 0, -0.01, 0.01], axis()))

    a3 = subplot(313, sharex=a1)
    step(th, map(lambda t: float(load(t*60*60)[0]), th))
    ylabel('Load flow')
    xlabel('Time (h)')
    axis(map(add, [0, 0, -0.01, 0.01], axis()))

    savefig('sim.png')

except Exception as e:
    print e
