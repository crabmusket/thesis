def xdot(sys):
    """
Returns a function of time, state and input that applies the system dynamics
and returns the current rate of change of the system (i.e., the xdot function).
    """
    (A, B, _, _) = sys
    def inner(t, x, u, *args):
        x_ = x.reshape(x.shape[0], 1)
        return A * x_ + B * u
    return inner
