from numpy import zeros
from numpy.linalg import norm
from math import pi, sqrt

# Implement the hot water tank model of \textcite{Cristofari02}.
def model(h, r, N, P, heat, getAmbient, getLoad):
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
    A_end = A1 + pi * r * r # Wall area of end segment
    U_s_int = A_int * U # Rate of temperature something
    U_s_end = A_end * U # Rate of temperature something else

    def controlBot(T_l, T, i):
        if i is 0:
            return 1 if T_l < T[i] else 0
        else:
            return 1 if T[i-1] <= T_l < T[i] else 0

    def controlTop(T_c, T, i):
        if i is N-1:
            return 1 if T_c > T[i] else 0
        else:
            return 1 if T[i+1] >= T_c > T[i] else 0

    def mflow(t, T, u, i):
        return getLoad(t)[0] * sum() -
               u[0]          * sum()

    # Rate of change
    def xdot(t, T, u):
        dT = zeros(T.shape)
        for i in range(N):
            # Ambient temperature loss
            U_amb = (U_s_end if i in [0, N-1] else U_s_int) * (getAmbient(t)[0] - x[i])
            U_input = 0
            U_mflow = 0

            # Final temperature change (\autoref{eq:node-dT})
            dT[i] = (U_amb + U_input + U_mflow) / (rho * C * v)
        return dT
    return xdot
