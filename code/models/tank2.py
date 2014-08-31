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

    def BLoad(T_l, T, i):
        if i is 0:
            return 1 if T_l < T[i] else 0
        else:
            return 1 if T[i-1] <= T_l < T[i] else 0

    def BColl(T_c, T, i):
        if i is N-1:
            return 1 if T_c > T[i] else 0
        else:
            return 1 if T[i+1] >= T_c > T[i] else 0

    # Net mass flow into node i from node i+1, i.e. in the direction of the
    # collector loop (downwards).
    def mflow(T, u, i, load, coll):
        return coll[0] * sum([BColl(coll[1], T, j) for j in range(i+1, N)]) \
             - load[0] * sum([BLoad(load[1], T, j) for j in range(0, i)])

    # Rate of change
    def xdot(t, T, u):
        dT = zeros(T.shape)
        load = getLoad(t)
        coll = getCollector(t)
        for i in range(N):
            # Ambient temperature loss
            U_amb = (U_s_end if i in [0, N-1] else U_s_int) * (getAmbient(t)[0] - T[i])

            # Temperature flow from collector/load inlets.
            U_inlet = BLoad(load[1], T, i) * load[0] * C * (load[1] - T[i]) \
                    + BColl(coll[1], T, i) * coll[0] * C * (coll[1] - T[i])

            # Mass flow.
            U_mflow = 0
            if i is 0:
                U_mflow = max(0, mflow(T, u, i, load, coll))   * C * (T[i+1] - T[i])
            elif i is N-1:
                U_mflow = min(0, mflow(T, u, i-1, load, coll)) * C * (T[i] - T[i-1])
            else:
                U_mflow = max(0, mflow(T, u, i, load, coll))   * C * (T[i+1] - T[i]) \
                        + min(0, mflow(T, u, i-1, load, coll)) * C * (T[i] - T[i-1])

            # Final temperature change (\autoref{eq:node-dT})
            dT[i] = (U_amb + U_inlet + U_mflow) / (rho * C * v)
        return dT
    return xdot
