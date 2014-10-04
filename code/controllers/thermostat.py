def thermostat(measure, on, off, setpoint, deadband):
    def controller(t, x):
        temp = x[measure]
        if controller.heating is False:
            if temp < setpoint-deadband:
                controller.heating = True
                return on
            else:
                return off
        else:
            if temp < setpoint:
                return on
            else:
                controller.heating = False
                return off
    controller.heating = False
    return controller
