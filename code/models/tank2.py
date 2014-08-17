from numpy import zeros
from numpy.linalg import norm
from math import pi, sqrt

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
    m = v * rho # Mass of each segment
    Pmcn = P / (m * c * len(heat)) # Rate of temperature something
    A1 = 2 * pi * r * d # Wall area of middle segment
    A2 = A1 + pi * r * r # Wall area of end segment
    U_s1 = (A1 * U) / (m * c) # Rate of temperature something
    U_s2 = (A2 * U) / (m * c) # Rate of temperature something else
    kpcd2 = k / (rho * c * d**2) # Rate of temperature something or other

    # Rate of change
    def xdot(t, x, u):
        dx = zeros(x.shape)
        for i in range(N):
			# Ambient temperature loss
            U_amb = (U_s1 if i in [0, N-1] else U_s2) * (getAmbient(t)[0] - x[i])
			U_input = 0
			U_mflow = 0

            # Final temperature change (\autoref{eq:node-dT})
            dx[i] = (u_amb + U_input + U_mflow) / (rho * C * v)
        return dx
    return xdot
