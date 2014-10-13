from numpy import array
from ..utils.time import hours_after_midnight
from datetime import datetime, timedelta
from ..utils.interval import Interval

fileStart = datetime(2014, 1, 1)

def make(start):
    hourlyAmbient = Interval()
    for line in open('data/ambient.txt', 'r'):
        temp = float(line)
        hourlyAmbient.const_for(temp, 1)

    def predictor(t):
        dt = timedelta(seconds=t)
        time = start - fileStart + dt
        hour = time.days * 24 + time.seconds / 60.0 / 60.0
        temp = hourlyAmbient(hour)
        return temp

    return predictor
