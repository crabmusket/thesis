def controller(measure, on, off, setpoint, deadband):
    def law(t, x):
        if hasattr(measure, '__call__'):
            val = measure(x)
        else:
            val = x[measure]
        if law.turnedOn is False:
            if val < setpoint-deadband:
                law.turnedOn = True
                return on
            else:
                return off
        else:
            if val < setpoint:
                return on
            else:
                law.turnedOn = False
                return off
    law.turnedOn = False
    law.on = on
    law.off = off
    law.setpoint = setpoint
    law.deadband = deadband
    return law
