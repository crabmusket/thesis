print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

from utils.interval import Interval
from numpy import array, linspace
from operator import add
from datetime import datetime

from models import tank2 as tank
from controllers.thermostat import thermostat
import prediction.ambient
import prediction.load
import prediction.collector
import simulation.nonlinear as simulation

print 'Beginning simulation'

startTime = datetime(2014, 9, 9, 00, 00, 00)
ambient = prediction.ambient.make(start = startTime)
load = prediction.load.make(start = startTime, mainsTemp = ambient)
collector = prediction.collector.make(start = startTime)

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
    getCollector = collector
)

dt = 30
tf = 60 * 60 * 24 * 7
x0 = array([24] * N).T
s = simulation.Run(
    xdot = tankModel,
    u = thermostat(
        measure = N-1,
        flow = 0.03,
        setpoint = 60,
        deadband = 5
    ),
    x0 = x0,
    dt = dt,
    tf = tf
)

(us, xs) = s.result()
ts = linspace(0, tf, num = len(xs[0,:]))
th = map(lambda t: t / (60.0*60), ts)

try:
    figure(figsize=(15, 20), dpi=80)

    a1 = subplot(411)
    ylabel('Tank temperatures')
    hs = [plot(th, xs[i,:])[0] for i in range(N)]
    ls = [str(i) for i in range(N)]
    axis(map(add, [0, 0, -1, 1], axis()))

    a2 = subplot(412, sharex=a1)
    ylabel('Control effort')
    for i in range(len(us[:,0])):
        step(th, us[i,:])
    axis(map(add, [0, 0, -0.002, 0.01], axis()))

    a3 = subplot(413, sharex=a1)
    ylabel('Load flow')
    step(th, map(lambda t: float(load(t*60*60)[0]), th))
    axis(map(add, [0, 0, -0.01, 0.01], axis()))

    a4 = subplot(414, sharex=a1)
    ylabel('Collector temperature')
    step(th, map(lambda t: float(collector(t*60*60)[1]), th))
    axis(map(add, [0, 0, -1, 1], axis()))

    xlabel('Simulation time (h)')

    savefig('sim.png')

except Exception as e:
    print e
