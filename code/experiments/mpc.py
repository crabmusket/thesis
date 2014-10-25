if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Simulate the MPC controller')

    parser.add_argument('--month',   default='jun', choices=['jan', 'jun'],
        help='Which month to start the simulation in.')
    parser.add_argument('--days',    default=8, type=int,
        help='Number of days the sinulation will run for.')
    parser.add_argument('--start',   type=int,
        help='Start graphing at the start of this day (indexed from 0).')
    parser.add_argument('--end',     type=int,
        help='End graphing at the end of this day (indexed from 0).')

    parser.add_argument('--width',   default=6, type=float,
        help='Width in inches of the resulting plot')
    parser.add_argument('--height',  default=4, type=float,
        help='height in inches of the resulting plot.')

    parser.add_argument('--cost',    default=1, type=float,
        help='Weight on the input term of the cost function.')
    parser.add_argument('--horizon', default=6, type=int,
        help='Number of hours to predict into the future.')
    parser.add_argument('--setpoint', default=55, type=int,
        help='Setpoint for internal tank thermostats.')
    parser.add_argument('--deadband', default=5,  type=int,
        help='Deadband for internal control thermostats.')
    parser.add_argument('--cset', default=8, type=int,
        help='Setpoint for differential collector thermostat.')
    parser.add_argument('--cdead', default=6, type=int,
        help='Deadband for differential collector thermostat.')

    parser.add_argument('--loadP',         default='data/daily_load.txt',
        help='File containing load prediction values.')
    parser.add_argument('--insolationP',   default='data/insolation.txt',
        help='File containing insolation prediction values.')
    parser.add_argument('--ambientP',      default='data/ambient.txt',
        help='File containing ambient prediction values.')

    parser.add_argument('--alltemps',      action='store_true',
        help='Show all tank temperatures, instead of just the top and bottom.')
    parser.add_argument('--internals',     action='store_true',
        help='Show controller\'s prediction of average temperature at each timestep.')

    parser.add_argument('name',
        help='Filename prefix for plot and results.')

    args = parser.parse_args()

print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

import warnings
warnings.simplefilter('ignore', np.ComplexWarning)

from ..utils.interval import Interval
from ..utils.time import hours_after_midnight
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

def run(startTime, args):
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
    H = args.horizon
    C = 2400
    UA = 0.5 * (2 * pi * r * h + 2 * pi * r * r)
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
        mainsTemp = ambientT,
        filename = 'data/daily_load3.txt',
    )
    loadP = load.predict(
        start = startTime,
        mainsTemp = ambientP,
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

    # Construct the objective function for one solve step of the controller.
    # The problem depends on R(t)
    def objective(t, y, u):
        R = co.matrix(diag(reference(t)))
        return cp.norm(R * cp.min_elemwise(y-50, 0)) \
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
        out['Ycost'] = norm(R.dot(minimum(y.value-50, 0)))

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

    def report(t, T, u):
        if t - report.lastTime >= 3600:
            report.lastTime = t
            now = datetime.now()
            print '{}\t{:.2f}'.format(int(t/3600.0), (now - report.lastWallTime).total_seconds())
            report.lastWallTime = now
        if loadT(t)[0] > 0:
            if T[N-1] >= 50:
                results['satisfied'] += dt
            else:
                results['unsatisfied'] += dt
        if u[0] > 0:
            results['energy'] += u[0] * P * dt / (3.6e6) # convert to kWh
        [m_aux, U_aux, m_coll, m_coll_return] = tankModel.lastInternalControl
        results['solar'] += m_coll * T[N+NC-1]
        results['auxiliary'] += m_aux * T[N+NC+NX-1]
    report.lastTime = 0
    report.lastWallTime = datetime.now()

    tf = 60 * 60 * 24 * args.days - dt
    x0 = array([24] * (N+NC+NX)).T
    s = nonlinear.Run(
        xdot = tankModel,
        u = controller,
        x0 = x0,
        dt = dt,
        tf = tf,
        report = report,
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

    figure(figsize=(args.width, args.height), dpi=80)

    a1 = subplot(311)
    ylabel('Tank (deg C)')
    if args.internals:
        [plotControl(h, plotControl.y) for h in range(hourFrom, hourTo)]
    if args.alltemps:
        temps = range(0, N)
    else:
        temps = [0, N-1]
    [plot(th, xs[i,:])[0] for i in temps]
    axis(map(add, [0, 0, -1, 1], axis()))

    a2 = subplot(312, sharex=a1)
    ylabel('Costs')
    [step(th, getControl(th, cost), label=cost) for cost in ['Ucost', 'Ycost']]
    legend()
    axis(map(add, [0, 0, -0.1, 0], axis()))

    a4 = subplot(313, sharex=a1)
    ylabel('Load and control')
    step(
        th,
        map(lambda t: float(loadP(t*60*60)[0]), th),
        label='Load flow'
    )
    for i in range(len(us[:,0])):
        step(
            th,
            map(lambda u: u/10.0, us[i,:]),
            label='Control signal'
        )
    axis(map(add, [0, 0, -0.01, 0.1], axis()))

    xlabel('Simulation time (h)')

    savefig(args.name+'.png')

    with open(args.name+'_results.txt', 'w') as f:
        if results['unsatisfied'] is 0:
            f.write('Satisfaction: {:.2f}%\n'.format(100))
        else:
            f.write('Satisfaction: {:.2f}%\n'.format(
                results['satisfied'] / float(results['satisfied'] + results['unsatisfied']) * 100
            ))
        f.write('Energy used: {:.2f}kWh\n'.format(
            results['energy']
        ))
        if results['auxiliary'] is 0:
            f.write('Solar fraction: {:.2f}%\n'.format(100))
        else:
            f.write('Solar fraction: {:.2f}%\n'.format(
                results['solar'] / float(results['solar'] + results['auxiliary']) * 100
            ))

if __name__ == '__main__':
    if args.month == 'jan':
        start = datetime(2014, 1, 1, 00, 00, 00)
    else:
        start = datetime(2014, 6, 1, 00, 00, 00)
    run(start, args)
