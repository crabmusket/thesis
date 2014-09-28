from numpy import zeros
from numpy.linalg import norm
from math import pi, sqrt

# Implement the hot water tank model of \textcite{Cristofari02} with addional
# collector and auxiliary heater modelling.
def model(h, r, NT, NC, NX, PX, auxOutlet, getAmbient, getLoad, getCollector):
    # Water and tank constants
    rho = 1000 # Water density
    C = 2400 # Specific heat capacity
    U = 0.5 # Tank wall heat loss coefficient
    k = 0.58 # Heat conductivity
    K = 0.41 # von Karman constant
    beta = 69e-6 # Thermal expansion coefficient
    g = 9.81 # Gravity

    # Derived parameters
    d = float(h) / NT # Depth of each segment
    v = pi * r * r * d # Volume of each segment
    A_int = 2 * pi * r * d # Wall area of interior segment
    A_end = A_int + pi * r * r # Wall area of end segment
    U_s_int = A_int * U # Rate of temperature something
    U_s_end = A_end * U # Rate of temperature something else

    # Inlet control for cold water entering the tank.
    def enterCold(T, T_l):
        if T_l < T[0]:
            return 0
        for i in range(1, NT):
            if T[i-1] <= T_l < T[i]:
                return i
        # Should never reach this.
        return 0

    # Inlet control for hot water entering the tank.
    def enterHot(T, T_c):
        if T_c > T[NT-1]:
            return NT-1
        for i in range(0, NT-1):
            if T[i+1] >= T_c > T[i]:
                return i 
        # We should never reach this default.
        return NT-1

    # Rate of change
    def xdot(t, T, u):
        dT = zeros(T.shape)

        # Get current load and disturbance conditions.
        load = getLoad(t)
        coll = getCollector(t)
        T_amb = getAmbient(t)[0]

        # Calculate the water temperature the aux heater will achieve, given its
        # inlet temperature, flow, and power rating.
        m_aux = max(0, u[0])
        T_aux = T[auxOutlet] + (PX / (m_aux * C) if m_aux > 0 else 0)

        # Layers where water enters the tank.
        i_coll = enterHot(T, coll[1])
        i_load = enterCold(T, load[1])
        i_aux = enterHot(T, T_aux)

        # Convenience functions.
        m  = lambda i: coll[0] * int(i <= i_coll) \
                     - load[0] * int(i >= i_load) \
                     + m_aux   * int(i_aux >= i >= auxOutlet)
        if load[0] > 0:
            print m(0)

        for i in range(0, NT):
            # Ambient temperature loss
            # TODO: fix ambient loss
            U_amb = (U_s_end if i in [0, NT-1] else U_s_int) * (T_amb - T[i])

            # Temperature flow from collector/load inlets.
            U_inlet = int(i_load == i) * load[0] * C * (load[1] - T[i]) \
                    + int(i_coll == i) * coll[0] * C * (coll[1] - T[i]) \
                    + int(i_aux == i)  * m_aux   * C * (T_aux   - T[i])

            # Mass flow.
            U_mflow = (min(0, m(i-1)) * C * (T[i] - T[i-1]) if i > 0 else 0) \
                    + (max(0, m(i))   * C * (T[i+1] - T[i]) if i < NT-1 else 0)

            # Final temperature change (\autoref{eq:node-dT})
            dT[i] = (U_amb + U_inlet + U_mflow) / (rho * C * v)
        return dT
    return xdot
