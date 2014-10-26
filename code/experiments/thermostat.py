if __name__ == '__main__':
    import sys
    import argparse
    from ..utils import options
    parser = argparse.ArgumentParser(description='Simulate the MPC controller')
    options.setup(parser)
    parser.add_argument('--cost', help='Does nothing.')
    args = parser.parse_args()

print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

from ..utils.interval import Interval
from ..utils.time import hours_after_midnight
from ..utils import report
from numpy import array, linspace, average, diag
from numpy.linalg import norm
from operator import add
from datetime import datetime
from math import sin, pi

import cvxopt as cvx
import cvxpy

from ..models import cristofariPlus, halvgaard
from ..controllers import thermostat, mpc, pwm
from ..prediction import insolation, ambient, load, collector
from ..simulation import nonlinear

def run(args):
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

    ambientT = ambient.predict(
        start = startTime,
        filename = 'data/ambient.txt',
    )

    def sunAngleFactor(start):
        def inner(t):
            h = hours_after_midnight(t, start)
            factor = 0 if h < 6 or h > 18 \
                else sin(h-6 / 12 * 2*pi) / 2 + 1
            return factor
        return inner

    insolationT = insolation.predict(
        start = startTime,
        angleFactor = sunAngleFactor(startTime),
        efficiency = nuC,
        area = area,
        filename = 'data/insolation.txt',
    )

    loadT = load.predict(
        start = startTime,
        mainsTemp = ambientT,
        filename = 'data/daily_load3.txt',
    )

    def loadHour(t):
        loads = [loadT(t+dt) for dt in range(0, 3600, 60)]
        avgFlow = sum([l[0] for l in loads]) / 60.0
        avgTemp = sum([l[1] for l in loads]) / 60.0
        return [avgFlow, avgTemp]

    tankModel = cristofariPlus.model(
        h = h, r = r, NT = N,
        NC = NC, NX = NX,
        collVolume = 0.8, auxVolume = 0.2,
        P = P,
        auxOutlet = auxOutlet,
        auxEfficiency = nuX,
        internalControl = True,
        setpoint = args.setpoint, deadband = args.deadband,
        collSetpoint = args.cset, collDeadband = args.cdead,
        getAmbient = ambientT,
        getLoad = loadT,
        getInsolation = insolationT,
    )

    controller = tankModel.internalController

    results = {
        'satisfied': 0,
        'unsatisfied': 0,
        'energy': 0,
        'solar': 0,
        'auxiliary': 0,
    }

    tf = 60 * 60 * 24 * days - dt
    x0 = array([24] * (N+NC+NX)).T
    s = nonlinear.Run(
        xdot = tankModel,
        u = controller,
        x0 = x0,
        dt = dt,
        tf = tf,
        report = report.to(results, tankModel, dt, loadT, N, NC, NX, P),
    )

    (us_, xs_) = s.result()

    if len(showRange) == 0:
        hourFrom = 0
        hourTo = int(tf / 60.0 / 60.0)
    else:
        hourFrom = 24 * showRange[0]
        hourTo = 24 * (showRange[-1]+1)
    plotFrom = int(hourFrom * 60 * 60 / dt)
    plotTo = int(hourTo * 60 * 60 / dt)
    us = us_[:, plotFrom:plotTo]
    xs = xs_[:, plotFrom:plotTo]
    ts = linspace(0, tf, num = len(xs[0,:]))
    th = map(lambda t: t / (60.0*60), ts)

    figure(figsize=(30, 15), dpi=80)

    ax = subplot(311)
    ax.set_xlim([hourFrom, hourTo])
    ylabel('Tank temperatures (deg C)')
    [plot(th, xs[i,:])[0] for i in [0, N-1]]
    axis(map(add, [0, 0, -1, 1], axis()))

    """
    ax = subplot(312, sharex=a1)
    ylabel('Heater and collector (deg C)')
    [plot(th, xs[i,:])[0] for i in [N, N+NC-1]]
    [plot(th, xs[i,:])[0] for i in [N+NC, N+NC+NX-1]]
    axis(map(add, [0, 0, -1, 1], axis()))
    """

    ax = subplot(312, sharex=a1)
    ylabel('Insolation (W)')
    step(th, map(lambda t: float(insolationT(t*60*60)), th))
    axis(map(add, [0, 0, -0.9, 0.5], axis()))

    ax = subplot(313, sharex=a1)
    ylabel('Load flow (L/s) and control signal')
    ax.step(th, map(lambda t: float(loadT(t*60*60)[0]), th))
    ax.axis(map(add, [0, 0, -0.1, 0.1], ax.axis()))
    ax = ax.twinx()
    [ax.step(th, us[i,:]) for i in range(len(us[:,0]))]
    ax.axis(map(add, [0, 0, -0.1, 0.1], ax.axis()))

    xlabel('Simulation time (h)')

    savefig(args.name+'.png')

    report.write(args.name+'.txt', results, args.verbose)

if __name__ == '__main__':
    run(args)
