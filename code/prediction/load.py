from datetime import datetime, timedelta
from ..utils.interval import Interval

fileStart = datetime(2014, 1, 1)

def predict(start, filename, mainsTemp=lambda *args: [20]):
    dailyLoad = Interval()
    maxUsage = 57000000
    C = 2400

    # Load pattern repeated daily.
    for line in open(filename, 'r'):
        (time, fraction) = map(float, line.split('\t'))
        # Convert from energy fraction to flow rate.
        mass = maxUsage * fraction / C / 55.0
        flow = mass / 360.0
        dailyLoad.const_til(flow, time)

    # Monthly variation in total usage.
    monthlyFraction = Interval()
    for line in open('data/monthly_load.txt', 'r'):
        (time, fraction) = map(float, line.split('\t'))
        monthlyFraction.const_til(fraction, time)

    def predictor(t):
        dt = timedelta(seconds=t)
        time = start - fileStart + dt
        hour = time.days * 24 + time.seconds / 60.0 / 60.0
        fraction = monthlyFraction(hour)
        flow = dailyLoad(hour % 24)
        return [flow, mainsTemp(t)]

    return predictor
