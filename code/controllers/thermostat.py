def controller(measure, on, off, setpoint, deadband):
    def law(t, x):
        temp = x[measure]
        if law.heating is False:
            if temp < setpoint-deadband:
                law.heating = True
                return on
            else:
                return off
        else:
            if temp < setpoint:
                return on
            else:
                law.heating = False
                return off
    law.heating = False
    law.on = on
    law.off = off
    law.setpoint = setpoint
    law.deadband = deadband
    return law
