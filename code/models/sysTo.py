def xdot(sys, dist=None):
    """
Returns a function of time, state and input that applies the system dynamics
and returns the current rate of change of the system (i.e., the xdot function).
    """
    (A, B, _, _) = sys
    def inner(t, x0, u, *args):
        x0 = x0.reshape(x0.shape[0], 1)
        x = A * x0 + B * u
        if dist is not None:
            x += dist(t, x0, u, *args)
        return x
    return inner
