if __name__ == '__main__':
    import sys
    import argparse
    from ..utils import options
    parser = argparse.ArgumentParser(description='Simulate the MPC controller')
    options.setup(parser)
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
    startTime = datetime(2014, args.month, args.day, 00, 00, 00)

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
        auxSetpoint = args.aset, auxDeadband = args.adead,
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

    tf = 60 * 60 * 24 * args.days - dt
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

    if args.start is None:
        hourFrom = 0
    else:
        hourFrom = 24 * args.start
    if args.end is None:
        hourTo = int(tf / 60.0 / 60.0)
    else:
        hourTo = 24 * (args.end+1)

    plotFrom = int(hourFrom * 60 * 60 / dt)
    plotTo = int(hourTo * 60 * 60 / dt)
    us = us_[:, plotFrom:plotTo]
    xs = xs_[:, plotFrom:plotTo]
    ts = linspace(hourFrom * 60 * 60, hourTo * 60 * 60, num = len(xs[0,:]))
    th = map(lambda t: t / (60.0*60), ts)

    ax = figure(figsize=(args.width, args.height), dpi=80)

    ax = subplot(311)
    ylabel('Tank (deg C)')
    [plot(th, xs[i,:])[0] for i in [0, N-1]]
    ax.set_xlim(hourFrom, hourTo)
    axis(map(add, [0, 0, -1, 1], axis()))

    """
    ax = subplot(312, sharex=a1)
    ylabel('Heater and collector (deg C)')
    [plot(th, xs[i,:])[0] for i in [N, N+NC-1]]
    [plot(th, xs[i,:])[0] for i in [N+NC, N+NC+NX-1]]
    axis(map(add, [0, 0, -1, 1], axis()))
    """

    ax = subplot(312, sharex=ax)
    ylabel('Insolation (W)')
    step(th, map(lambda t: float(insolationT(t*60*60)), th))
    ax.set_xlim(hourFrom, hourTo)
    axis(map(add, [0, 0, -0.9, 0.5], axis()))

    ax = subplot(313, sharex=ax)
    ax.set_ylabel('Load flow (L/s)')
    ax.step(th, map(lambda t: float(loadT(t*60*60)[0]), th))
    ax.axis(map(add, [0, 0, -0.01, 0.03], ax.axis()))
    ax.set_xlim(hourFrom, hourTo)
    for tl in ax.get_yticklabels():
        tl.set_color('b')
    ax = ax.twinx()
    ax.set_ylabel('Control signal')
    for i in range(len(us[:,0])):
       ax.step(th, us[i,:], 'g')
    for tl in ax.get_yticklabels():
        tl.set_color('g')
    ax.axis(map(add, [0, 0, -0.05, 0.05], ax.axis()))
    ax.set_xlim(hourFrom, hourTo)

    xlabel('Simulation time (h)')

    savefig(args.name+'.png')

    report.write(args.name+'.txt', results, args.verbose)

if __name__ == '__main__':
    run(args)
