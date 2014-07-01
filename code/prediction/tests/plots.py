import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as p
import datetime as dt

from .. import load
(ts, vs) = load.predictedFrom(
    time=dt.datetime(2014, 7, 1, 04, 00, 00),
    over=dt.timedelta(hours=12),
    interval=dt.timedelta(minutes=10))
p.figure(1)
try:
    p.plot_date(mpl.dates.date2num(ts), vs)
    p.savefig('load.png')
except: pass
