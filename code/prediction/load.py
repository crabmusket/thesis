from ..utils.interval import Interval
from numpy import array

def make(start, mainsTemp=None, numPeople=1):
    if mainsTemp is None:
        mainsTemp = lambda *args: [24]

    def seconds_after_midnight(t):
        return 60*60*start.hour \
             + 60*start.minute \
             + start.second + t \
             + 1e-6*start.microsecond
    hours_after_midnight = lambda t: seconds_after_midnight(t)/60/60

    n = numPeople
    # Water flow intervals.
    flow = Interval() \
            .const_til(0,        7) \
            .const_for(7.0/60.0, 10.0*n/60.0) \
            .const_til(0,        20) \
            .const_for(7.0/60.0, 10.0*n/60.0) \
            .const_til(0,        24)

    def predictor(t):
        return array([
            flow(hours_after_midnight(t) % 24),
            mainsTemp(t)
        ])
    return predictor
