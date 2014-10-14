from ..utils.time import hours_after_midnight
from ..utils.interval import Interval
from numpy import array

def predict(start):
    gpm_sf = 0.025 # gallons per minute per square foot
    ratio = 0.6791 # to litres per second per square meter
    sq_m = 2 # collector area
    flow = gpm_sf * ratio * sq_m # litres per second

    panel = Interval(array) \
            .const_til([0, 30], 6) \
            .const_til([flow, 30], 8) \
            .const_til([flow, 40], 10) \
            .const_til([flow, 50], 12) \
            .const_til([flow, 70], 14) \
            .const_til([flow, 60], 16) \
            .const_til([flow, 40], 18) \
            .const_til([flow, 30], 20) \
            .const_til([0, 30], 24)

    def predictor(t):
        return panel(hours_after_midnight(t, start) % 24)
    return predictor
