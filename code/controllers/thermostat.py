from numpy import array
def thermostat(measure, flow, setpoint, deadband):
    def controller(x, t):
        temp = x[measure]
        if controller.heating is False:
            if temp < setpoint-deadband:
                controller.heating = True
                return array([flow])
            else:
                return array([0.0])
        else:
            if temp < setpoint:
                return array([flow])
            else:
                controller.heating = False
                return array([0.0])
    controller.heating = False
    return controller
