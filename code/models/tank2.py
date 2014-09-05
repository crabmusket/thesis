from numpy import zeros
from numpy.linalg import norm
from math import pi, sqrt

# Implement the hot water tank model of \textcite{Cristofari02}.
def model(h, r, N, P, getAmbient, getLoad, getCollector):
    # Water and tank constants
    rho = 1000 # Water density
    C = 2400 # Specific heat capacity
    U = 0.5 # Tank wall heat loss coefficient
    k = 0.58 # Heat conductivity
    K = 0.41 # von Karman constant
    beta = 69e-6 # Thermal expansion coefficient
    g = 9.81 # Gravity

    # Derived parameters
    d = float(h) / N # Depth of each segment
    v = pi * r * r * d # Volume of each segment
    A_int = 2 * pi * r * d # Wall area of interior segment
    A_end = A_int + pi * r * r # Wall area of end segment
    U_s_int = A_int * U # Rate of temperature something
    U_s_end = A_end * U # Rate of temperature something else

    # Inlet control for cold water entering the tank.
    def ctrlCold(T_l, T, i):
        if i is 0:
            return 1 if T_l < T[i] else 0
        else:
            return 1 if T[i-1] <= T_l < T[i] else 0

    # Inlet control for hot water entering the tank.
    def ctrlHot(T_c, T, i):
        if i is N-1:
            return 1 if T_c > T[i] else 0
        else:
            return 1 if T[i+1] >= T_c > T[i] else 0

    # Net mass flow into node i from node i+1, i.e. in the direction of the
    # collector loop (downwards).
    def mflow(T, u, i, load, coll):
        return coll[0] * sum([BColl(coll[1], T, j) for j in [N-1] + range(i+1, N-1)]) \
             - load[0] * sum([BLoad(load[1], T, j) for j in [0] + range(1, i-1)])

    # Rate of change
    def xdot(t, T, u):
        dT = zeros(T.shape)
        load = getLoad(t)
        coll = getCollector(t)
        m  = lambda i: mflow(T, u, i, load, coll)
        Bl = lambda i: ctrlCold(load[1], T, i)
        Bc = lambda i: ctrlHot (coll[1], T, i)

        for i in range(0, N):
            # Ambient temperature loss
            U_amb = (U_s_end if i in [0, N-1] else U_s_int) * (getAmbient(t)[0] - T[i])

            # Temperature flow from collector/load inlets.
            U_inlet = Bl(i) * load[0] * C * (load[1] - T[i]) \
                    + Bc(i) * coll[0] * C * (coll[1] - T[i])

            # Mass flow.
            U_mflow = (min(0, m(i-1)) * C * (T[i] - T[i-1]) if i > 0 else 0) \
                    + (max(0, m(i))   * C * (T[i+1] - T[i]) if i < N-1 else 0)

            # Final temperature change (\autoref{eq:node-dT})
            dT[i] = (U_amb + U_inlet + U_mflow) / (rho * C * v)
        return dT
    return xdot
