def controller(modulation, period, postprocess):
    def control(t, x):
        if t - control.lastTime >= period:
            control.lastModulation = modulation(t, x)
            if control.lastModulation > 1e-4:
                control.lastSignal = postprocess(1)
            else:
                control.lastModulation = 0
            control.lastTime = t
        if t - control.lastTime >= period * control.lastModulation:
            control.lastSignal = postprocess(0)
        return control.lastSignal

    control.lastTime = -period
    return control
