from numpy import array
from math import pi, cos

# Ambient temperature shall be a sine wave with peak at 12 noon and trough at 12
# midnight. Nothing too complicated.
def make(start, minimum=10, maximum=26):
    def seconds_after_midnight(t):
        return 60*60*start.hour \
             + 60*start.minute \
             + start.second + t \
             + 1e-6*start.microsecond

    def predictor(t):
        x = seconds_after_midnight(t) / (60*60*24) * 2 * pi
        return array([minimum + (1-cos(x))/2 * (maximum - minimum)])
    return predictor
