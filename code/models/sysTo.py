def xdot(sys, dist=None):
    """
Returns a function of time, state and input that applies the system dynamics
and returns the current rate of change of the system (i.e., the xdot function).
    """
    (A, Bu, Bd, _, _) = sys
    def inner(t, x0, u, *args):
        x0 = x0.reshape(x0.shape[0], 1)
        x = A * x0 + Bu * u
        if dist is not None:
            x += Bd * dist(t, x0, *args)
        return x
    return inner
