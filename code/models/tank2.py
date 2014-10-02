from numpy import zeros
from numpy.linalg import norm
from math import pi, sqrt

# Implement the hot water tank model of \textcite{Cristofari02}.
def model(h, r, NT, NC, NX, P, vC, vX, auxOutlet, \
        auxPumpController, auxHeatController, collPumpController, \
        getAmbient, getLoad, getInsolation):
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
    vC_ = vC / NC # Volume per segment in collector
    vX_ = vX / NX # Volume per segment in aux heater
    A_int = 2 * pi * r * d # Wall area of interior segment
    A_end = A_int + pi * r * r # Wall area of end segment
    U_s_int = A_int * U # Rate of temperature something
    U_s_end = A_end * U # Rate of temperature something else
    U_s_x = 0
    U_s_c = 0

    # Inlet control for cold water entering the tank.
    def ctrlCold(T_l, T, i):
        if i is 0:
            return 1 if T_l <= T[i] else 0
        else:
            return 1 if T[i-1] < T_l <= T[i] else 0

    # Inlet control for hot water entering the tank.
    def ctrlHot(T_c, T, i):
        if i is NT-1:
            return 1 if T_c >= T[i] else 0
        else:
            return 1 if T[i+1] > T_c >= T[i] else 0

    # Net mass flow into node i from node i+1, i.e. in the direction of the
    # collector loop (downwards).
    def mflow(T, u, i, load, coll, aux):
        return coll[0] * sum([ctrlHot (coll[1], T, j) for j in [NT-1] + range(i+1, N-1)]) \
             - load[0] * sum([ctrlCold(load[1], T, j) for j in [0] + range(1, i-1)]) \
             + aux[0] * (int(i >= auxOutlet) - \
                         sum([ctrlHot(aux[1],  T, j) for j in [0] + range(1, i+1)]))

    # Rate of change
    def xdot(t, T, u):
        dT = zeros(T.shape)

        # Calculate collector state change
        NC_ = NT + NC
        T_coll = T[NC_-1]
        m_coll = collPumpController(T)
        for i in range(NT+1, NC_):
            pass

        # Calculate heater state change
        NX_ = NC_ + NX
        T_aux = T[NX_-1]
        m_aux = auxPumpController(T)
        for i in range(NC_, NX_):
            pass

        # Get current load and disturbance conditions.
        load = getLoad(t)
        T_a = getAmbient(t)[0]
        coll = 0
        aux = [m_aux, T_aux]

        # Calculate the water temperature the aux heater will achieve, given its
        # inlet temperature, flow, and power rating.
        m_aux = max(0, u[0])
        T_aux = T[auxOutlet] + (P / (m_aux * C) if m_aux > 0 else 0)

        # Convenience functions.
        m  = lambda i: mflow(T, u, i, load, coll, aux)
        Bl = lambda i: ctrlCold(load[1], T, i)
        Bc = lambda i: ctrlHot (coll[1], T, i)
        Bu = lambda i: ctrlHot (aux[1],  T, i)

        for i in range(0, NT):
            # Ambient temperature loss
            U_amb = (U_s_end if i in [0, NT-1] else U_s_int) * (T_a - T[i])

            # Temperature flow from collector/load inlets.
            U_inlet = Bl(i) * load[0] * C * (load[1] - T[i]) \
                    + Bc(i) * coll[0] * C * (coll[1] - T[i]) \
                    + Bu(i) * aux[0]  * C * (aux[1]  - T[i])

            # Mass flow.
            U_mflow = (min(0, m(i-1)) * C * (T[i] - T[i-1]) if i > 0 else 0) \
                    + (max(0, m(i))   * C * (T[i+1] - T[i]) if i < NT-1 else 0)

            # Final temperature change (\autoref{eq:node-dT})
            dT[i] = (U_amb + U_inlet + U_mflow) / (rho * C * v)

        return dT
    return xdot
