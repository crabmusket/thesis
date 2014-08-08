def xdot(sys, dist=None):
    """
Returns a function of time, state and input that applies the system dynamics
and returns the current rate of change of the system (i.e., the xdot function).
    """
    (A, Bu, Bd, _, _) = sys
    def inner(t, x0, u, *args):
        x = A.dot(x0) + Bu.dot(u)
        if dist is not None:
            x += Bd.dot(dist(t, x0, *args))
        return x
    return inner
