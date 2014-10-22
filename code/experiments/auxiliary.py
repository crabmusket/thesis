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

def run(chargeHours, waitHours, dischargeHours, name):
    # Tank parameters
    N = 20
    NC = 10
    NX = 10
    r = 0.3
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

    loadP_ = Interval() \
        .const_til(array([0.0, 24]), chargeHours + waitHours) \
        .const_for(array([0.05, 24]), dischargeHours) \
        .const_til(array([0.0, 24]), 1)
    loadP = lambda t: loadP_(t/60.0/60.0)

    insolationP = lambda *args: 0,

    controller_ = Interval() \
        .const_for(array([1]), chargeHours) \
        .const_for(array([0]), 1)
    controller = lambda t, x: controller_(t/60.0/60.0)

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

    tf = 60 * 60 * (chargeHours+waitHours+dischargeHours) - dt
    x0 = array([24] * (N+NC+NX)).T
    s = nonlinear.Run(
        xdot = tankModel,
        u = controller,
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

    a1 = subplot(311)
    ylabel('Tank temperatures (deg C)')
    [plot(th, xs[i,:])[0] for i in range(0, N)]
    axis(map(add, [0, 0, -1, 1], axis()))

    a2 = subplot(312, sharex=a1)
    ylabel('Heater temperatures (deg C)')
    [plot(th, xs[i,:])[0] for i in range(N+NC, N+NC+NX)]
    axis(map(add, [0, 0, -1, 1], axis()))

    a4 = subplot(313, sharex=a1)
    ylabel('Load flow (L/s) and control signal')
    step(th, map(lambda t: float(loadP(t*60*60)[0]), th))
    [step(th, map(lambda u: u/10.0, us[i,:])) for i in range(len(us[:,0]))]
    axis(map(add, [0, 0, -0.1, 0.1], axis()))

    xlabel('Simulation time (h)')

    savefig(name)

import sys
if __name__ == '__main__':
    [_, chargeHours, waitHours, dischargeHours, name] = sys.argv
    run(int(chargeHours), int(waitHours), int(dischargeHours), name+'.png')
