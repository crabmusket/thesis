from numpy import zeros
from numpy.linalg import norm
from math import pi, sqrt

def model(h, r, N, P, heat, getAmbient, getLoad):
    # Water and tank constants
    rho = 1000 # Water density
    c = 2400 # Specific heat capacity
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
    A1Umc = (A1 * U) / (m * c) # Rate of temperature something
    A2Umc = (A2 * U) / (m * c) # Rate of temperature something else
    kpcd2 = k / (rho * c * d**2) # Rate of temperature something or other

    # Buoyancy factor (\autoref{eq:epsilon})
    Kdl2 = (K * 2*r)**2
    gb = g * beta
    def epsilon(x, i):
        # Rough temperature gradient
        if i is 0:
            dTi = (x[1] - x[0]) / d
        elif i is N-1:
            dTi = (x[N-1] - x[N-2]) / d
        else:
            dTu = (x[i+1] - x[i]) / d
            dTl = (x[i] - x[i-1]) / d
            dTi = (dTu + dTl) / 2
        print dTi
        return Kdl2 * sqrt(gb * dTi)

    # Rate of change
    def xdot(t, x, u):
        dx = zeros(x.shape)
        for i in range(N):
            # External factors (\autoref{eq:flow-ext})
            AUmc = A2Umc if i in [0, N-1] else A1Umc
            dt_ext = AUmc * (getAmbient(t)[0] - x[i])
            if i in heat:
                dt_ext += Pmcn * u[0]

            # Mixing between layers (\autoref{eq:flow-mix})
            dt_mix = kpcd2 + epsilon(x, i)
            if i is 0:
                dt_mix *= x[1] - x[0]
            elif i is N-1:
                dt_mix *= x[N-1] - x[N-2]
            else:
                dt_mix *= x[i+1] - 2*x[i] + x[i-1]

            # Mass flow (\autoref{eq:flow-mflow})
            dt_mflow = 0

            # Final temperature change (\autoref{eq:flow-total})
            dx[i] = dt_ext + dt_mix + dt_mflow
        return dx
    return xdot
