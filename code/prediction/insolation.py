from datetime import datetime, timedelta
from ..utils.interval import Interval

fileStart = datetime(2014, 1, 1)

def make(start, efficiency, angleFactor):
    hourlyInsolation = Interval()
    for line in open('data/insolation.txt', 'r'):
        solar = map(float, line.split('\t'))
        hourlyInsolation.const_for(solar, 1)

    def predictor(t):
        dt = timedelta(seconds=t)
        time = start - fileStart + dt
        hour = time.days * 24 + time.seconds / 60.0 / 60.0
        ins = hourlyInsolation(hour)
        return (ins[0] + ins[1] * angleFactor(hour)) * efficiency

    return predictor
