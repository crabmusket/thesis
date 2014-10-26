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
from numpy import array, linspace, average, diag, minimum
from numpy.linalg import norm
from operator import add
from datetime import datetime
from math import sin, pi

import cvxopt as co
import cvxpy as cp

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
    r = 0.3
    h = 1.3
    P = 3000
    auxOutlet = N/2
    nuX = 1

    # Collector parameters
    area = 5
    nuC = 0.5

    # Simulation timestep
    dt = 60

    # MPC parameters
    H = args.horizon
    C = 2400
    UA = 10 * (2 * pi * r * h + 2 * pi * r * r)
    rho = 1000
    m = pi * r * r * h * rho

    # True and predicted ambient temperature.
    ambientT = ambient.predict(start = startTime, filename = 'data/ambient.txt')
    ambientP = ambient.predict(start = startTime, filename = args.ambientP)

    def sunAngleFactor(start):
        def inner(t):
            h = hours_after_midnight(t, start)
            factor = 0 if h < 6 or h > 18 \
                else sin(h-6 / 12 * 2*pi) / 2 + 1
            return factor
        return inner

    # True and predicted insolation profiles.
    insolationT = insolation.predict(
        start = startTime,
        angleFactor = sunAngleFactor(startTime),
        efficiency = nuC,
        area = area,
        filename = 'data/insolation.txt',
    )
    insolationP = insolation.predict(
        start = startTime,
        angleFactor = sunAngleFactor(startTime),
        efficiency = nuC,
        area = area,
        filename = args.insolationP,
    )

    # True and predicted load profiles.
    loadT = load.predict(
        start = startTime,
        mainsTemp = lambda t: ambientT(t) * 0.25 + 20 * 0.75,
        filename = 'data/daily_load3.txt',
    )
    loadP = load.predict(
        start = startTime,
        mainsTemp = lambda t: ambientT(t) * 0.25 + 20 * 0.75,
        filename = args.loadP,
    )

    # Used by the controller to get the mean load over an hour. Uses loadP
    # instead of loadT because the prediction may differ from the actuality.
    def loadHour(t):
        loads = [loadP(t+dt) for dt in range(0, 3600, 60)]
        avgFlow = sum([l[0] for l in loads]) / 60.0
        avgTemp = sum([l[1] for l in loads]) / 60.0
        return [avgFlow, avgTemp]

    # Create the model which simulates the entire system.
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
        # Tank receives true disturbances.
        getAmbient = ambientT,
        getLoad = loadT,
        getInsolation = insolationT,
    )

    Tobj = 50
    # Construct the objective function for one solve step of the controller.
    # The problem depends on R(t)
    def objective(t, y, u):
        R = co.matrix(diag(reference(t)))
        return cp.norm(R * cp.min_elemwise(y-Tobj, 0)) \
             + cp.norm(u, 1) * args.cost

    # The reference vector used buy the objective function. This reference is
    # only 1 for the hours starting at 6am, 7am, 4pm, 5pm and 6pm.
    def reference(t):
        def mask(t):
            hour = hours_after_midnight(t, startTime) % 24
            # Only consider reference during the peak times of the day.
            return (1 if 6 <= hour <= 7 or 16 <= hour <= 18 else 0)
        times = map(lambda h: h * 3600 + t, range(1, H+1))
        return [mask(tt) for tt in times]

    # Get a vector of disturbances for the control problem. We use the
    # predictors, not the true values.
    def disturbances(t, x):
        load = loadHour(t)
        return array([
            [load[0]],
            [load[0] * load[1]],
            [insolationP(t)],
            [ambientP(t)],
        ])

    # Callback to analyse the controller's action at a given point.
    def analyse(out, t, x, y, u, dists):
        R = diag(reference(t))
        out['Ucost'] = norm(u.value, 1)
        out['Ycost'] = norm(R.dot(minimum(y.value-Tobj, 0)))
        out['u'] = float(u.value[0])

    controlOutputs = []
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
                    0 <= u, u <= 1,
                ],
                disturbances = disturbances,
                outputs = controlOutputs,
                analysis = analyse,
            ),
            preprocess = average,
        ),
        postprocess = lambda u: array([u]),
    )

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

    def plotControl(hour, fn):
        control = controlOutputs[hour]
        th = range(hour + 1, hour + 1 + H)
        plot(th, fn(control), 'm')
    plotControl.u = lambda c: c['input'].reshape((H,)).tolist()[0]
    plotControl.y = lambda c: c['output'].reshape((H,)).tolist()[0]

    def getControl(th, param):
        return map(lambda h: controlOutputs[int(h)][param], th)

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
    if args.internals:
        [plotControl(h, plotControl.y) for h in range(hourFrom, hourTo)]
    if args.alltemps:
        temps = range(0, N)
    else:
        temps = [0, N-1]
    [plot(th, xs[i,:])[0] for i in temps]
    ax.set_xlim(hourFrom, hourTo)
    axis(map(add, [0, 0, -1, 1], axis()))

    ax = subplot(312, sharex=ax)
    ax.set_ylabel('Input cost')
    ax.step(th, getControl(th, 'Ucost'))
    for tl in ax.get_yticklabels():
        tl.set_color('b')
    ax.axis(map(add, [0, 0, -0.1, 0], ax.axis()))
    ax.set_xlim(hourFrom, hourTo)
    ax = ax.twinx()
    ax.set_ylabel('State cost')
    ax.step(th, getControl(th, 'Ycost'), 'g')
    for tl in ax.get_yticklabels():
        tl.set_color('g')
    ax.set_xlim(hourFrom, hourTo)
    ax.axis(map(add, [0, 0, -0.1, 0], ax.axis()))

    ax = subplot(313, sharex=ax)
    ax.set_ylabel('Load flow (L/s)')
    ax.step(th, map(lambda t: float(loadT(t*60*60)[0]), th))
    ax.axis(map(add, [0, 0, -0.01, 0.03], ax.axis()))
    ax.set_xlim(hourFrom, hourTo)
    for tl in ax.get_yticklabels():
        tl.set_color('b')
    ax = ax.twinx()
    ax.set_ylabel('Control signal')
    ax.step(th, getControl(th, 'u'), 'g')
    #for i in range(len(us[:,0])):
    #   ax.step(th, us[i,:], 'g')
    for tl in ax.get_yticklabels():
        tl.set_color('g')
    ax.axis(map(add, [0, 0, -0.05, -0.01], ax.axis()))
    ax.set_xlim(hourFrom, hourTo)

    xlabel('Simulation time (h)')

    savefig(args.name+'.png')

    report.write(args.name+'.txt', results, args.verbose)

if __name__ == '__main__':
    run(args)
