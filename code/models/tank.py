from numpy import zeros
from numpy.linalg import norm
from math import pi

def model(h, r, N, P, heat, getAmbient, getLoad):
    # Water and tank constants
    rho = 1000 # Water density
    c = 2400 # Specific heat capacity
    U = 0.5 # Tank wall heat loss coefficient

    # Derived parameters
    d = float(h) / N # Depth of each segment
    v = pi * r * r * d # Volume of each segment
    m = v * rho # Mass of each segment
    nel = len(heat) # Number of segments heated
    Pmcn = P / (m * c * nel) # Rate of temperature something
    A1 = 2 * pi * r * d # Wall area of middle segment
    A2 = A1 + pi * r * r # Wall area of end segment
    A1Umc = (A1 * U) / (m * c) # Rate of temperature something
    A2Umc = (A2 * U) / (m * c) # Rate of temperature something else

    # Rate of change
    def xdot(t, x, u):
        xd = zeros(x.shape)
        for i in range(N):
            AUmc = A2Umc if i in [0, N-1] else A1Umc
            dt_ext = AUmc * (getAmbient(t)[0] - x[i])
            if i in heat:
                dt_ext += Pmcn * u[0]
            dt_mix = 0
            dt_mflow = 0
            xd[i] = dt_ext + dt_mix + dt_mflow
        return xd
    return xdot
