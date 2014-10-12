print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

from utils.interval import Interval
from utils.time import hours_after_midnight
from numpy import array, linspace, average, diag
from operator import add
from datetime import datetime
from math import sin, pi

import cvxopt as cvx
import cvxpy

from models import cristofariPlus, halvgaard
from controllers import thermostat, mpc, pwm
import prediction.insolation
import prediction.ambient
import prediction.load2
import prediction.collector
import simulation.nonlinear as simulation

startTime = datetime(2014, 1, 1, 00, 00, 00)

ambient = prediction.ambient.make(start = startTime)

def sunAngleFactor(start):
    def inner(t):
        h = hours_after_midnight(t, start)
        factor = 0 if h < 6 or h > 18 \
            else sin(h-6 / 12 * 2*pi) / 2 + 1
        return factor
    return inner

area = 5
nuC = 0.5
insolation = prediction.insolation.make(
    start = startTime,
    angleFactor = sunAngleFactor(startTime),
    efficiency = nuC,
    area = area,
)

load = prediction.load2.make(
    start = startTime,
    mainsTemp = ambient,
)

def loadHour(t):
    loads = [load(t+dt) for dt in range(0, 3600, 60)]
    avgFlow = sum([l[0] for l in loads]) / 60.0
    avgTemp = sum([l[1] for l in loads]) / 60.0
    return [avgFlow, avgTemp]

N = 20
NC = 10
NX = 10
r = 0.4
h = 1.3
P = 2000
auxOutlet = N/2
nuX = 0.5
tankModel = cristofariPlus.model(
    h = h, r = r, NT = N,
    NC = NC, NX = NX,
    collVolume = 0.8, auxVolume = 0.2,
    P = P,
    auxOutlet = auxOutlet,
    auxEfficiency = nuX,
    auxThermostat = False,
    getAmbient = ambient,
    getLoad = load,
    getInsolation = insolation,
)

def objective(t, y, u):
    R = cvx.matrix(diag(reference(t)))
    return cvxpy.norm(R * (y-60)) + cvxpy.norm(u, 1)

def disturbances(t, x):
    load = loadHour(t)
    return array([
        [load[0]],
        [load[0] * load[1]],
        [insolation(t)],
        [ambient(t)],
    ])

H = 6
def reference(t):
    def mask(t):
        hour = hours_after_midnight(t, startTime) % 24
        return (1 if 7 <= hour <= 12 else 0)
    times = map(lambda h: h * 3600 + t, range(1, H+1))
    return [mask(tt) for tt in times]

C = 2400
UA = 0.5 * (2 * pi * r * h + 2 * pi * r * r)
rho = 1000
m = pi * r * r * h * rho
controller = pwm.controller(
    period = 600,
    modulation = mpc.controller(
        period = 3600,
        law = mpc.LTI(
            horizon = H,
            step = 3600,
            system = halvgaard.model(
                m, C, UA, P,
                auxEfficiency = nuX,
            ),
            objective = objective,
            constraints = lambda t, y, u: [
                #y <= 70,
                0 <= u, u <= 1,
            ],
            disturbances = disturbances,
        ),
        preprocess = average,
    ),
    postprocess = lambda u: array([u]),
)

"""
controller = thermostat.controller(
    measure = N/2,
    on  = array([1]),
    off = array([0]),
    setpoint = 55,
    deadband = 5
)
"""

def report(t):
    print t

dt = 60
tf = 60 * 60 * 24 * 7 - dt
x0 = array([24] * (N+NC+NX)).T
s = simulation.Run(
    xdot = tankModel,
    u = controller,
    x0 = x0,
    dt = dt,
    tf = tf,
    #report = report,
)

def run():
    return s.result()

def view((us_, xs_), hourFrom=None, hourTo=None, size=(30, 15), dpi=80, fname = 'sim.png'):
    if hourFrom is not None and hourTo is not None:
        plotFrom = int(hourFrom * 60 * 60 / dt)
        plotTo = int(hourTo * 60 * 60 / dt)
        us = us_[:, plotFrom:plotTo]
        xs = xs_[:, plotFrom:plotTo]
        ts = linspace(plotFrom*dt, plotTo*dt, num = len(xs[0,:]))
    else:
        (us, xs) = (us_, xs_)
        ts = linspace(0, tf, num = len(xs[0,:]))

    th = map(lambda t: t / (60.0*60), ts)

    figure(figsize=size, dpi=dpi)

    a1 = subplot(411)
    ylabel('Tank temperatures (deg C)')
    [plot(th, xs[i,:])[0] for i in [0, N-1]]
    axis(map(add, [0, 0, -1, 1], axis()))

    a2 = subplot(412, sharex=a1)
    ylabel('Heater and collector (deg C)')
    [plot(th, xs[i,:])[0] for i in range(N, N+NC)]
    [plot(th, xs[i,:])[0] for i in range(N+NC, N+NC+NX)]
    axis(map(add, [0, 0, -1, 1], axis()))

    a3 = subplot(413, sharex=a1)
    ylabel('Load flow (L/s)')
    step(th, map(lambda t: float(load(t*60*60)[0]), th))
    axis(map(add, [0, 0, -0.01, 0.01], axis()))

    a4 = subplot(414, sharex=a1)
    ylabel('Control effort')
    [step(th, us[i,:]) for i in range(len(us[:,0]))]
    axis(map(add, [0, 0, -0.1, 0.1], axis()))

    """
    ylabel('Insolation (W)')
    step(th, map(lambda t: float(insolation(t*60*60)), th))
    axis(map(add, [0, 0, -0.9, 0.5], axis()))
    """

    xlabel('Simulation time (h)')

    savefig(fname)

if __name__ == '__main__':
    R = run()
