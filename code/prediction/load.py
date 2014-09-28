from ..utils.time import hours_after_midnight
from ..utils.interval import Interval
from numpy import array

# Water flow intervals.
patterns = [
    # 10-minute showers at 7am and 8pm
    Interval() \
        .const_til(0,        7) \
        .const_for(7.0/60.0, 10.0/60.0) \
        .const_til(0,        20) \
        .const_for(7.0/60.0, 10.0/60.0) \
        .const_til(0,        24),
    Interval() \
        .const_til(0,        7) \
        .const_for(7.0/60.0, 10.0/60.0) \
        .const_til(0,        20) \
        .const_for(7.0/60.0, 10.0/60.0) \
        .const_til(0,        24),
]

def make(start, mainsTemp=None, users=[0]):
    if mainsTemp is None:
        mainsTemp = lambda *args: [24]

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
