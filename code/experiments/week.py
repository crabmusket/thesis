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

from ..models import cristofariPlus, halvgaard
from ..controllers import thermostat, mpc, pwm
from ..prediction import insolation, ambient, load2, collector
from ..simulation import nonlinear

def run(startTime, useMPC, days, name):
    N = 20
    NC = 10
    NX = 10
    r = 0.4
    h = 1.3
    P = 3000
    auxOutlet = N/2
    nuX = 0.8

    area = 5
    nuC = 0.5
    H = 6

    # Simulation timestep
    dt = 60

    # MPC parameters
    C = 2400
    UA = 0.5 * (2 * pi * r * h + 2 * pi * r * r)
    rho = 1000
    m = pi * r * r * h * rho

    ambientP = ambient.predict(start = startTime)

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

    loadP = load2.predict(
        start = startTime,
        mainsTemp = ambientP,
    )

    def loadHour(t):
        loads = [loadP(t+dt) for dt in range(0, 3600, 60)]
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
        getAmbient = ambientP,
        getLoad = loadP,
        getInsolation = insolationP,
    )

    def objective(t, y, u):
        R = cvx.matrix(diag(reference(t)))
        return cvxpy.norm(R * (y-50)) + cvxpy.norm(u, 1)

    def disturbances(t, x):
        load = loadHour(t)
        return array([
            [load[0]],
            [load[0] * load[1]],
            [insolationP(t)],
            [ambientP(t)],
        ])

    def reference(t):
        def mask(t):
            hour = hours_after_midnight(t, startTime) % 24
            # Only consider reference during the peak times of the day.
            return (1 if 6 <= hour <= 8 or 16 <= hour <= 18 else 0)
        times = map(lambda h: h * 3600 + t, range(1, H+1))
        return [mask(tt) for tt in times]

    def analyse(out, t, x, y, u, dists):
        R = diag(reference(t))
        out['Ucost'] = norm(u.value)
        out['Ycost'] = norm(R.dot(y.value-60))

    controlOutputs = []
    if useMPC:
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
                    outputs = controlOutputs,
                    analysis = analyse,
                ),
                preprocess = average,
            ),
            postprocess = lambda u: array([u]),
        )
    else:
        controller = tankModel.auxPump

    results = {
        'satisfied': 0,
        'unsatisfied': 0,
        'energy': 0,
    }

    def report(t, T, u):
        if t - report.lastTime >= 3600:
            print t
            report.lastTime = t
        if loadP(t)[0] > 0:
            if T[N-1] >= 50:
                results['satisfied'] += dt
            else:
                results['unsatisfied'] += dt
        if u[0] > 0:
            results['energy'] += u[0] * P * dt
    report.lastTime = 0

    tf = 60 * 60 * 24 * days - dt
    x0 = array([24] * (N+NC+NX)).T
    s = nonlinear.Run(
        xdot = tankModel,
        u = controller,
        x0 = x0,
        dt = dt,
        tf = tf,
        report = report,
    )

    (us, xs) = s.result()

    def plotControl(hour, fn):
        control = controlOutputs[hour]
        th = range(hour + 1, hour + 1 + H)
        plot(th, fn(control), 'm')
    plotControl.y = lambda c: c['output'].reshape((H,)).tolist()[0]

    def getControl(th, param):
        return map(lambda h: controlOutputs[int(h)][param], th)

    hourFrom = 0
    hourTo = int(tf / 60.0 / 60.0)
    ts = linspace(0, tf, num = len(xs[0,:]))
    th = map(lambda t: t / (60.0*60), ts)

    figure(figsize=(30, 15), dpi=80)

    a1 = subplot(411)
    ylabel('Tank temperatures (deg C)')
    if len(controlOutputs) > 0:
        [plotControl(h, plotControl.y) for h in range(hourFrom, hourTo)]
    [plot(th, xs[i,:])[0] for i in range(0, N)]
    axis(map(add, [0, 0, -1, 1], axis()))

    a2 = subplot(412, sharex=a1)
    if len(controlOutputs) > 0:
        ylabel('Costs')
        [step(th, getControl(th, cost), label=cost) for cost in ['Ucost', 'Ycost']]
        legend()
        axis(map(add, [0, 0, -0.1, 0], axis()))
    else:
        ylabel('Heater and collector (deg C)')
        [plot(th, xs[i,:])[0] for i in [N, N+NC-1]]
        [plot(th, xs[i,:])[0] for i in [N+NC, N+NC+NX-1]]
        axis(map(add, [0, 0, -1, 1], axis()))

    a3 = subplot(413, sharex=a1)
    ylabel('Insolation (W)')
    step(th, map(lambda t: float(insolationP(t*60*60)), th))
    axis(map(add, [0, 0, -0.9, 0.5], axis()))

    a4 = subplot(414, sharex=a1)
    ylabel('Load flow (L/s) and control signal')
    step(th, map(lambda t: float(loadP(t*60*60)[0]), th))
    [step(th, map(lambda u: u/10.0, us[i,:])) for i in range(len(us[:,0]))]
    axis(map(add, [0, 0, -0.1, 0.1], axis()))

    xlabel('Simulation time (h)')

    savefig(name)

    with open(name+'_results.txt', 'w') as f:
        if results['unsatisfied'] is 0:
            f.write('Satisfaction: {}%\n'.format(100))
        else:
            f.write('Satisfaction: {}%\n'.format(
                results['satisfied'] / float(results['satisfied'] + results['unsatisfied']) * 100
            ))
        f.write('Energy used: {}kWh\n'.format(
            results['energy'] / (3.6e6)
        ))

import sys
if __name__ == '__main__':
    [_, month, method] = sys.argv
    if month == 'jan':
        start = datetime(2014, 1, 1, 00, 00, 00)
    else:
        start = datetime(2014, 6, 1, 00, 00, 00)
    useMPC = method == 'mpc'
    run(start, useMPC, days=7, name=method+'_'+month)
