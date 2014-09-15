from ..utils.time import hours_after_midnight
from ..utils.interval import Interval
from numpy import array

def make(start, mainsTemp=None):
    if mainsTemp is None:
        mainsTemp = lambda *args: [24]

    # Water flow intervals.
    flow = Interval() \
            .const_til(0,        7) \
            .const_for(7.0/60.0, 10.0/60.0) \
            .const_til(0,        20) \
            .const_for(7.0/60.0, 10.0/60.0) \
            .const_til(0,        24)

    def predictor(t):
        return array([
            flow(hours_after_midnight(t, start) % 24),
            mainsTemp(t)
        ])
    return predictor
