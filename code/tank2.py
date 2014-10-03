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
import cvxopt as cvx

from models import tank2 as tank
import models.halvgaard
from controllers.thermostat import thermostat
import controllers.mpc
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
NC = 10
NX = 10
r = 0.4
h = 1.3
auxOutlet = N/2
tankModel = tank.model(
    h = h, r = r, NT = N,
    NC = NC, NX = NX,
    auxOutlet = auxOutlet,
    getAmbient = ambient,
    getLoad = load,
    getCollector = collector
)

auxPump = thermostat(
    measure = 0,
    on = 0.05,
    off = 0,
    setpoint = 60,
    deadband = 5
)

P = 2000
auxHeat_ = thermostat(
    measure = 0,
    on = P,
    off = 0,
    setpoint = 60,
    deadband = 5
)
auxHeat = lambda T, t, md_x: 0 if md_x == 0 else auxHeat_(T, t)

H = 12
Q = cvx.matrix(kron(eye(H), diag([0]*(N-1) + [1] + [0]*N)))
predictive = mpc.controller(
    period = 3600,
    horizon = H,
    system = halvgaard.model(),
    constraints = lambda X, y, u: [],
    disturbances = lambda t, x: 0
)

def collPump(T, t):
    pass

def controllers(T, t):
    fraction = predictive(T, t)
    md_x = auxPump(T, t)
    (md_coll_tank, md_coll_coll) = collPump(T, t)
    p_x = auxHeat(fraction, md_x)
    return array([md_x, p_x, md_coll_tank, md_coll_coll])

dt = 5
tf = 60 * 60 * 24 * 2
x0 = array([24] * N).T
s = simulation.Run(
    xdot = tankModel,
    u = controllers,
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
