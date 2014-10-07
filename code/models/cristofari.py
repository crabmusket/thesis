from numpy import zeros
from numpy.linalg import norm
from math import pi, sqrt

# Implement the hot water tank model of \textcite{Cristofari02}.
def model(h, r, N, P, auxOutlet,
        collRate, collArea,
        collEfficiency, auxEfficiency,
        getAmbient, getLoad, getInsolation, sunAngleFactor):
    # Water and tank constants
    rho = 1000 # Water density
    C = 2400 # Specific heat capacity
    U = 0.5 # Tank wall heat loss coefficient

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
    def mflow(T, i, m_c, m_l, m_x, Bl, Bc, Bx):
        return m_c * sum([Bc(j) for j in [N-1] + range(i+1, N-1)]) \
             - m_l * sum([Bl(j) for j in [0] + range(1, i-1)]) \
             + m_x * (int(i >= auxOutlet) - \
                      sum([Bx(j) for j in [0] + range(1, i+1)]))

    # Rate of change
    def xdot(t, T, u):
        dT = zeros(T.shape)

        # Get current load and disturbance conditions.
        T_a = getAmbient(t)
        ins = getInsolation(t)
        load = getLoad(t)
        m_load = load[0]
        T_load = load[1]

        # Convert MJ/hour/sqm to Watts.
        watts = 277.8 # \url{http://www.wolframalpha.com/input/?i=megajoule%2Fhour}
        U_ins = ins * collEfficiency * watts * collArea

        # Calculate water temperature achieved by the collector. \todo{need a better
        # controller here, I assume}
        m_coll = collRate if U_ins > 0 else 0
        T_coll = T[0]# + (U_ins / (m_coll * C) if m_coll > 0 else 0)
        
        # Accommodate heater efficiency.
        U_aux = P * auxEfficiency

        # Calculate the water temperature the aux heater will achieve, given its
        # inlet temperature, flow, and power rating.
        m_aux = 0.05 * u
        T_aux = T[auxOutlet]# + (U_aux / (m_aux * C) if m_aux > 0 else 0)

        # Convenience functions.
        Bl = lambda i: ctrlCold(T_load, T, i)
        Bc = lambda i: ctrlHot (T_coll, T, i)
        Bx = lambda i: ctrlHot (T_aux,  T, i)
        m  = lambda i: mflow(T, i, m_coll, m_load, m_aux, Bl, Bc, Bx)

        for i in range(0, N):
            # Ambient temperature loss
            U_amb = (U_s_end if i in [0, N-1] else U_s_int) * (T_a - T[i])

            # Temperature flow from collector/load inlets.
            U_inlet = Bl(i) * m_load * C * (T_load - T[i]) \
                    + Bc(i) * m_coll * C * (T_coll - T[i]) \
                    + Bx(i) * m_aux  * C * (T_aux   - T[i])

            # Mass flow.
            U_mflow = (min(0, m(i-1)) * C * (T[i] - T[i-1]) if i > 0 else 0) \
                    + (max(0, m(i))   * C * (T[i+1] - T[i]) if i < N-1 else 0)

            # Final temperature change (\autoref{eq:node-dT})
            dT[i] = (U_amb + U_inlet + U_mflow) / (rho * C * v)
        return dT
    return xdot
