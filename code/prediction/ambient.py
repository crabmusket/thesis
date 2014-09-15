from numpy import array
from math import pi, cos
from ..utils.time import seconds_after_midnight

# Ambient temperature shall be a sine wave with peak at 12 noon and trough at 12
# midnight. Nothing too complicated.
def make(start, minimum=10, maximum=26):
    sam = lambda t: seconds_after_midnight(t, start)
    def predictor(t):
        x = sam(t) / (60*60*24) * 2 * pi
        return array([minimum + (1-cos(x))/2 * (maximum - minimum)])
    return predictor
