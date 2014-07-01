import numpy as np
import datetime as dt
from math import ceil, sin, pi
from itertools import islice
from ..utils import iterate, take

def predictedFrom(time, over, interval):
    steps = ceil(over.total_seconds() / interval.total_seconds())
    times = take(steps, iterate(lambda t: t + interval, time))
    values = map(lambda t: predictedAt(t), times)
    return (times, values)

directPeak   = 10
indirectPeak = 2
secsPerDay = 86400.0
morning = dt.timedelta(hours=6)
def predictedAt(time):
    direct   = max(0, sin(secs(time-morning)/secsPerDay * 2*pi) - 0.4)/0.4 * directPeak
    indirect = max(0, sin(secs(time-morning)/secsPerDay * 2*pi)) * indirectPeak
    return direct + indirect

def secs(time):
    return time.hour * 60 * 60 + time.minute * 60 + time.second
