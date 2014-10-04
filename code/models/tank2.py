from numpy import zeros
from numpy.linalg import norm
from math import pi, sqrt
from ..controllers.thermostat import thermostat

# Implement the hot water tank model of \textcite{Cristofari02}.
def model(h, r, NT, NC, NX, P, vC, vX, auxOutlet, \
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

    tankFirst = 0
    tankLast = NT-1
    collFirst = NT
    collLast = NT+NC-1
    auxFirst = NT+NC
    auxLast = NT+NC+NX-1

    # The auxiliary pump controller decides when to send water through the aux
    # loop to be heated. This is a simple thermostat controller which measures
    # temperature at the bottom of the tank.
    auxPump_ = thermostat(
        measure = tankFirst,
        on  = 0.05,
        off = 0,
        setpoint = 60,
        deadband = 5
    )
    auxPump = lambda u, t, T: 0 if u == 0 else auxPump_(t, T)

    # The auxiliary heater controller is responsible for heating the water
    # flowing through the auxiliary loop. If there is no flow it turns off,
    # otherwise using a thermostat to measure the temperature of the water being
    # sent back to the tank.
    auxHeat_ = thermostat(
        measure = auxLast,
        on  = P,
        off = 0,
        setpoint = 60,
        deadband = 5
    )
    auxHeat = lambda m_aux, t, T: 0 if m_aux == 0 else auxHeat_(t, T)

    # The collector pump controller returns two values - the flow to send back
    # into the tank, and the flow to bypass the tank and return to the collector
    # directly. It turns off entirely at night.
    collPump_ = thermostat(
        measure = collLast,
        on  = (0.05, 0),
        off = (0, 0.05),
        setpoint = 60,
        deadband = 5
    )
    collPump = collPump_ # TODO turn off at night

    # Inlet control for cold water entering the tank.
    def ctrlCold(T_l, T, i):
        if i is tankFirst:
            return 1 if T_l <= T[i] else 0
        else:
            return 1 if T[i-1] < T_l <= T[i] else 0

    # Inlet control for hot water entering the tank.
    def ctrlHot(T_c, T, i):
        if i is tankLast:
            return 1 if T_c >= T[i] else 0
        else:
            return 1 if T[i+1] > T_c >= T[i] else 0

    # Net mass flow into node i from node i+1, i.e. in the direction of the
    # collector loop (downwards).
    def mflow(T, i, m_c, m_l, m_x, Bl, Bc, Bx):
        return m_c * sum([Bc(j) for j in [NT-1] + range(i+1, NT-1)]) \
             - m_l * sum([Bl(j) for j in [0] + range(1, i-1)]) \
             + m_x * (int(i >= auxOutlet) - \
                        sum([Bx(j) for j in [0] + range(1, i+1)]))

    def xdot(t, T, u):
        dT = zeros(T.shape)

        # Get current load and disturbance conditions.
        T_a = getAmbient(t)
        ins = getInsolation(t)
        load = getLoad(t)
        m_load = load[0]
        T_load = load[1]

        # Compute internal control.
        m_aux = auxPump(u, t, T)
        p_aux = auxHeat(m_aux, t, T)
        (m_coll, m_coll_return) = collPump(t, T)

        # Calculate collector state change.
        T_coll = T[collLast]
        for i in range(collFirst, collFirst+NC):
            dT[i] = ins / (rho * C * vX) / NC * 0.1 # TODO magic 0.1
            if i is collFirst:
                dT[i] += m_coll        * C * (T[tankFirst] - T[i]) \
                       + m_coll_return * C * (T[collLast] - T[i])
            else:
                dT[i] += (m_coll + m_coll_return) * C * (T[i-1] - T[i])

        # Calculate heater state change.
        T_aux = T[auxLast]
        for i in range(auxFirst, auxFirst+NX):
            dT[i] = p_aux / (rho * C * vX)
            if i is auxFirst:
                dT[i] += m_aux * C * (T[auxOutlet] - T[i])
            else:
                dT[i] += m_aux * C * (T[i-1] - T[i])

        # Convenience functions.
        Bl = lambda i: ctrlCold(T_load, T, i)
        Bc = lambda i: ctrlHot (T_coll, T, i)
        Bx = lambda i: ctrlHot (T_aux,  T, i)
        m  = lambda i: mflow(T, i, m_coll, m_load, m_aux, Bl, Bc, Bx)

        # Calculate tank state change.
        for i in range(tankFirst, tankFirst+NT):
            # Ambient temperature loss
            # TODO: fix ends
            U_amb = (U_s_int if i in [tankFirst, tankLast] else U_s_int) \
                  * (T_a - T[i])

            # Temperature flow from collector/load inlets.
            U_inlet = Bl(i) * m_load * C * (T_load - T[i]) \
                    + Bc(i) * m_coll * C * (T_coll - T[i]) \
                    + Bx(i) * m_aux  * C * (T_aux  - T[i])

            # Mass flow.
            U_mflow = (min(0, m(i-1)) * C * (T[i] - T[i-1]) if i > 0 else 0) \
                    + (max(0, m(i))   * C * (T[i+1] - T[i]) if i < NT-1 else 0)

            # Final temperature change (\autoref{eq:node-dT})
            dT[i] = ((U_amb + U_inlet + U_mflow) / (rho * C * v))[0] # >:(

        return dT
    return xdot
