from ..utils.time import hours_after_midnight
from ..utils.interval import Interval
from numpy import array

# Liters per minute to liters per second.
Lpm = lambda l: l / float(60.0)
# Minutes to hours.
minutes = lambda m: m / float(60.0)

# Single spike profile.
def spike(start, duration, flow):
    return Interval() \
        .const_til(0, start) \
        .const_for(flow, duration) \
        .const_til(0, 24)

def make(start, profile, mainsTemp=None):
    if mainsTemp is None:
        mainsTemp = lambda *args: [24]

    # Concatenate multiuple profile functions into a single function.
    cat = lambda intervals: lambda t: sum([i(t) for i in intervals])
    profileC = [cat(ps) for ps in profile]

    def predictor(t):
        hour = hours_after_midnight(t, start)
        day = int(hour / 24)
        flow = profileC[day](hour % 24)
        return array([flow, mainsTemp(t)])
    return predictor
