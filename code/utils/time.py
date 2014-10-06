def seconds_after_midnight(t, base):
    return 60*60*base.hour \
         + 60*base.minute \
         + base.second + t \
         + 1e-6*base.microsecond

def hours_after_midnight(t, start):
    return seconds_after_midnight(t, start)/60.0/60.0
