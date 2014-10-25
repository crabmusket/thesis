if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Simulate the MPC controller')

    parser.add_argument('--month',   default=6, type=int,
        help='Which month to start the simulation in.')
    parser.add_argument('--day',     default=1, type=int,
        help='Which day of the month to start the simulation on.')

    parser.add_argument('--days',    default=8, type=int,
        help='Number of days the sinulation will run for.')

    parser.add_argument('--width',   default=6, type=float,
        help='Width in inches of the resulting plot')
    parser.add_argument('--height',  default=4, type=float,
        help='height in inches of the resulting plot.')

    parser.add_argument('--loadT',         default='data/daily_load.txt',
        help='File containing load prediction values.')
    parser.add_argument('--insolationT',   default='data/insolation.txt',
        help='File containing insolation prediction values.')
    parser.add_argument('--ambientT',      default='data/ambient.txt',
        help='File containing ambient prediction values.')

    parser.add_argument('name',
        help='Filename prefix for plot and results.')

    args = parser.parse_args()

print 'Loading modules'
import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

from numpy import linspace
from datetime import datetime
from ..utils.time import hours_after_midnight
from operator import add

from ..prediction import insolation, ambient, load, collector

def run(startTime, args):
    print 'Beginning plots'
    # Collector parameters
    area = 5
    nuC = 0.5

    ambientT = ambient.predict(
        start = startTime,
        filename = args.ambientT,
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
        filename = args.insolationT,
    )

    loadT = load.predict(
        start = startTime,
        mainsTemp = ambientT,
        filename = args.loadT,
    )

    tf = 60 * 60 * 24 * args.days
    hourFrom = 0
    hourTo = int(tf / 60.0 / 60.0)

    ts = linspace(hourFrom * 60 * 60, hourTo * 60 * 60, hourTo*60)
    th = map(lambda t: t / (60.0*60), ts)

    ax = subplot(311)
    ylabel('Insolation (W)')
    step(th, map(lambda t: float(insolationT(t*60*60)), th))
    axis(map(add, [0, 0, -0.9, 0.5], axis()))

    ax = subplot(312, sharex=ax)
    ylabel('Ambient (C)')
    plot(th, map(lambda t: float(ambientT(t*60*60)), th))
    axis(map(add, [0, 0, -1, 1], axis()))

    ax = subplot(313, sharex=ax)
    ylabel('Load flow (L/s)')
    ax.step(th, map(lambda t: float(loadT(t*60*60)[0]), th))
    ax.axis(map(add, [0, 0, -0.01, 0.03], ax.axis()))

    xlabel('Simulation time (h)')

    savefig(args.name+'.png')

import sys
if __name__ == '__main__':
    start = datetime(2014, args.month, args.day, 00, 00, 00)
    run(start, args)
