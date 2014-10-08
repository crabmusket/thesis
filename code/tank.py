print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

from utils.interval import Interval
from utils.time import hours_after_midnight
from numpy import array, linspace, average
from operator import add
from datetime import datetime
from math import sin, pi

import cvxopt as cvx
import cvxpy

from models import cristofari, halvgaard
from controllers import mpc
import prediction.insolation
import prediction.ambient
import prediction.load
from prediction.load import spike, Lpm, minutes
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

insolation = prediction.insolation.make(
    start = startTime,
    angleFactor = sunAngleFactor(startTime),
)

# Let's go with a 4-person household. Using information from YVW, we'll make up
# some schedules. Significant events: weekend showers are more spread out. One
# adult stays home on Wednesday. Evening showers on a couple of days.
# http://www.yvw.com.au/Home/Inyourhome/Understandingyourwateruse/index.htm
loadProfile = [
    # Monday
    [
        # Morning showers
        spike(7,   minutes(8),  Lpm(5)),
        spike(7.5, minutes(9),  Lpm(6)),
        spike(7.9, minutes(7),  Lpm(4)),
        spike(8.1, minutes(10), Lpm(5)),
        # Dishwasher
        spike(22.5, minutes(70), Lpm(0.3)),
    ],
    # Tuesday
    [
        # Morning showers
        spike(7.5, minutes(7), Lpm(4)),
        spike(7.2, minutes(8), Lpm(4)),
        spike(7.9, minutes(6), Lpm(5)),
        spike(8.5, minutes(6), Lpm(6)),
    ],
    # Wednesday
    [
        # Morning showers
        spike(6.8, minutes(8), Lpm(5)),
        spike(7.1, minutes(5), Lpm(4)),
        spike(7.8, minutes(9), Lpm(6)),
        spike(8.2, minutes(6), Lpm(5)),
        # Dishwasher
        spike(22.4, minutes(70), Lpm(0.3)),
    ],
    # Thursday
    [
        # Morning showers
        spike(6.5, minutes(8),  Lpm(4)),
        spike(7,   minutes(8),  Lpm(5)),
        spike(7.2, minutes(10), Lpm(6)),
        spike(7.6, minutes(8),  Lpm(7)),
        # Dishwasher
        spike(22.5, minutes(70), Lpm(0.3)),
    ],
    # Friday
    [
        # Morning showers
        spike(7,   minutes(8), Lpm(6)),
        spike(7.5, minutes(7), Lpm(5)),
        spike(7.9, minutes(5), Lpm(5)),
        spike(8.1, minutes(9), Lpm(7)),
    ],
    # Saturday
    [
        # Morning showers
        spike(8.2,   minutes(16), Lpm(6)),
        spike(9.1, minutes(7),  Lpm(5)),
        spike(9.5, minutes(11), Lpm(5)),
        spike(10.5, minutes(12), Lpm(7)),
        # Dishwasher
        spike(21.7, minutes(70), Lpm(0.3)),
    ],
    # Sunday
    [
        # 'Morning' showers
        spike(8.6,  minutes(8),  Lpm(6)),
        spike(9.8,  minutes(13), Lpm(5)),
        spike(10.5, minutes(19),  Lpm(5)),
        spike(13.2, minutes(14), Lpm(7)),
        # Dishwasher
        spike(21, minutes(70), Lpm(0.3)),
    ]
]

load = prediction.load.make(
    start = startTime,
    mainsTemp = ambient,
    profile = loadProfile + loadProfile # Two weeks, yeah
)

N = 20
r = 0.4
h = 1.3
P = 2000
nuC = 0.5
nuX = 0.5
area = 5
auxOutlet = N/2
tankModel = cristofari.model(
    h = h, r = r, N = N, P = P,
    auxOutlet = auxOutlet,
    collRate = 1, collArea = area,
    collEfficiency = nuC, auxEfficiency = nuX,
    getAmbient = ambient, getLoad = load, getInsolation = insolation,
    sunAngleFactor = sunAngleFactor(startTime),
)

H = 12
C = 2400
UA = 0.5 * (2 * pi * r * h + 2 * pi * r * r)
controller = mpc.controller(
    period = 3600,
    law = mpc.LTI(
        horizon = H,
        step = 3600,
        system = halvgaard.model(
            C, UA, P,
            collEfficiency = nuC, auxEfficiency = nuX,
            collArea = area,
            sunAngleFactor = sunAngleFactor(startTime),
        ),
        objective = lambda X, y: cvxpy.norm(y-60),
        constraints = lambda X, y, u: [
            y <= 70,
            0 <= u, u <= 1,
        ],
        disturbances = lambda t, x: array([
            [load(t)[0]],
            [load(t)[0] * load(t)[1]],
            [insolation(t)],
            [ambient(t)],
        ]),
    ),
    preprocess = lambda x: average(x),
    pwm = True,
)

dt = 60
tf = 60 * 60 * 12 - dt
x0 = array([24] * N).T
s = simulation.Run(
    xdot = tankModel,
    u = lambda *args: array([1]),
    x0 = x0,
    dt = dt,
    tf = tf
)

us_ = xs_ = None

def run():
    global us_
    global xs_
    (us_, xs_) = s.result()

def viewHours((us_, xs_), hourFrom, hourTo, size=(15, 20), dpi=80, fname = 'sim.png'):
    plotFrom = int(hourFrom * 60 * 60 / dt)
    plotTo = int(hourTo * 60 * 60 / dt)

    us = us_[:, plotFrom:plotTo]
    xs = xs_[:, plotFrom:plotTo]
    ts = linspace(plotFrom*dt, plotTo*dt, num = len(xs[0,:]))
    th = map(lambda t: t / (60.0*60), ts)

    figure(figsize=size, dpi=dpi)

    a1 = subplot(411)
    ylabel('Tank temperatures (deg C)')
    hs = [plot(th, xs[i,:])[0] for i in range(N)]
    ls = [str(i) for i in range(N)]
    axis(map(add, [0, 0, -1, 1], axis()))

    a2 = subplot(412, sharex=a1)
    ylabel('Control effort')
    [step(th, us[i,:]) for i in range(len(us[:,0]))]
    axis(map(add, [0, 0, -0.002, 0.01], axis()))

    a3 = subplot(413, sharex=a1)
    ylabel('Load flow (L/s)')
    step(th, map(lambda t: float(load(t*60*60)[0]), th))
    axis(map(add, [0, 0, -0.01, 0.01], axis()))

    a4 = subplot(414, sharex=a1)
    ylabel('Insolation (MJ/hour)')
    step(th, map(lambda t: float(insolation(t*60*60)), th))
    axis(map(add, [0, 0, -0.9, 0.5], axis()))

    xlabel('Simulation time (h)')

    savefig(fname)
