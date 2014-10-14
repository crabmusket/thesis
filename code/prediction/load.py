from datetime import datetime, timedelta
from ..utils.interval import Interval

fileStart = datetime(2014, 1, 1)

def predict(start, mainsTemp=lambda *args: [24]):
    dailyLoad = Interval()
    maxUsage = 57000000
    C = 2400
    for line in open('data/daily_load.txt', 'r'):
        (time, fraction) = map(float, line.split('\t'))
        mass = maxUsage * fraction / C / 55.0
        flow = mass / 360.0
        dailyLoad.const_til(flow, time)

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
