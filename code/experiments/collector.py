print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

from ..utils.interval import Interval
from ..utils.time import hours_after_midnight
from numpy import array, linspace, average, diag
from numpy.linalg import norm
from operator import add
from datetime import datetime
from math import sin, pi

import cvxopt as cvx
import cvxpy

from ..models import cristofariPlus
from ..simulation import nonlinear
from ..prediction import insolation

def run(startTime, name):
    # Tank parameters
    N = 20
    NC = 10
    NX = 10
    r = 0.4
    h = 1.3
    P = 3000
    auxOutlet = N/2
    nuX = 0.8

    # Collector parameters
    area = 5
    nuC = 0.5

    # Simulation timestep
    dt = 60

    # MPC parameters
    H = 6
    C = 2400
    UA = 0.5 * (2 * pi * r * h + 2 * pi * r * r)
    rho = 1000
    m = pi * r * r * h * rho

    ambientP = lambda *args: 24
    loadP = lambda *args: array([0.0, 24])

    def sunAngleFactor(start):
        def inner(t):
            h = hours_after_midnight(t, start)
            factor = 0 if h < 6 or h > 18 \
                else sin(h-6 / 12 * 2*pi) / 2 + 1
            return factor
        return inner

    insolationP = insolation.predict(
        start = startTime,
        angleFactor = sunAngleFactor(startTime),
        efficiency = nuC,
        area = area,
    )

    tankModel = cristofariPlus.model(
        h = h, r = r, NT = N,
        NC = NC, NX = NX,
        collVolume = 0.8, auxVolume = 0.2,
        P = P,
        auxOutlet = auxOutlet,
        auxEfficiency = nuX,
        internalControl = True,
        getAmbient = ambientP,
        getLoad = loadP,
        getInsolation = insolationP,
    )

    def report(t, T, u):
        if t - report.lastTime >= 3600:
            report.lastTime = t
            print t
    report.lastTime = 0

    tf = 60 * 60 * 24 - dt
    x0 = array([24] * (N+NC+NX)).T
    s = nonlinear.Run(
        xdot = tankModel,
        u = lambda *args: [0],
        x0 = x0,
        dt = dt,
        tf = tf,
        report = report,
    )

    us, xs = s.result()

    hourFrom = 0
    hourTo = int(tf / 60.0 / 60.0)
    ts = linspace(0, tf, num = len(xs[0,:]))
    th = map(lambda t: t / (60.0*60), ts)

    figure(figsize=(15, 10), dpi=80)

    a1 = subplot(211)
    ylabel('Tank temperatures (deg C)')
    [plot(th, xs[i,:])[0] for i in range(0, N)]
    axis(map(add, [0, 0, -1, 1], axis()))

    a2 = subplot(212, sharex=a1)
    ylabel('Collector temperatures (deg C)')
    [plot(th, xs[i,:])[0] for i in range(N, N+NC)]
    axis(map(add, [0, 0, -1, 1], axis()))

    xlabel('Simulation time (h)')

    savefig(name)

import sys
if __name__ == '__main__':
    [_, month, name] = sys.argv
    if month == 'jan':
        start = datetime(2014, 1, 1, 00, 00, 00)
    else:
        start = datetime(2014, 6, 1, 00, 00, 00)
    run(start, name+'.png')
