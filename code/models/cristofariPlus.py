from numpy import zeros, array
from numpy.linalg import norm
from math import pi, sqrt
from ..controllers import thermostat
from ..utils.time import hours_after_midnight
from math import sin, pi

# Implement the hot water tank model of \textcite{Cristofari02}.
def model(h, r, NT, NC, NX, P, collVolume, auxVolume, auxOutlet,
        auxEfficiency, internalControl,
        setpoint, deadband,
        collSetpoint, collDeadband,
        auxSetpoint, auxDeadband,
        getAmbient, getLoad, getInsolation):
    # Water and tank constants
    rho = 1000 # Water density
    C = 2400 # Specific heat capacity
    U = 10 # Tank wall heat loss coefficient, W/sqm

    # Derived parameters
    d = float(h) / NT # Depth of each segment
    vT = pi * r * r * d # Volume of each segment in tank
    vC = collVolume / NC # Volume per segment in collector
    vX = auxVolume / NX # Volume per segment in aux heater
    A_int = 2 * pi * r * d # Wall area of interior segment
    A_end = A_int + pi * r * r # Wall area of end segment
    U_s = (A_int + A_end / (NT/2)) * U # Rate of temperature something
    U_s_x = 0.5 / NX
    U_s_c = 1 / NC

    m_aux_on = 0.05 # Aux pump flow.
    m_coll_on = 0.02 # Collector flow

    # Node numbers for different areas of the tank. These index into the state
    # vector and label specific nodes in the heat flow simulation.
    tankFirst = 0
    tankLast = NT-1
    collFirst = NT
    collLast = NT+NC-1
    auxFirst = NT+NC
    auxLast = NT+NC+NX-1

    # The auxiliary pump controller decides when to send water through the aux
    # loop to be heated. This is a simple thermostat controller which measures
    # temperature at the bottom of the tank. If external control is off, then
    # it is forced off.
    auxPump = thermostat.controller(
        measure = tankLast,
        on  = array([1]),
        off = array([0]),
        setpoint = setpoint,
        deadband = deadband,
    )

    # The auxiliary heater controller is responsible for heating the water
    # flowing through the auxiliary loop. If there is no flow it turns off,
    # otherwise using a thermostat to measure the temperature of the water being
    # sent back to the tank.
    auxHeat_ = thermostat.controller(
        measure = auxLast,
        on  = P, # Power input when heating
        off = 0,
        setpoint = auxSetpoint,
        deadband = auxDeadband,
    )
    # Two cases: if there is mass flow, use the thermostat. No mass flow, no heat.
    auxHeat = lambda m_aux, t, T: 0 if m_aux == 0 else auxHeat_(t, T)

    # The collector pump controller returns two values - the flow to send back
    # into the tank, and the flow to bypass the tank and return to the collector
    # directly. It turns off entirely at night.
    collPump_ = thermostat.controller(
        measure = lambda T: T[collLast] - T[tankFirst],
        on  = (0, m_coll_on), # When we are 'on', i.e. the tank doesn't want our
        off = (m_coll_on, 0), # water, send the water back to the collector.
        setpoint = collSetpoint,
        deadband = collDeadband,
    )
    collPump = collPump_ # TODO turn off at night?

    # Inlet control for cold water entering the tank. Returns 1 at if cold water
    # should be deposited into node i, given the temperature distribution in T.
    def ctrlCold(T_c, T, i):
        if i is tankFirst:
            return 1 if T_c <= T[i] else 0
        else:
            return 1 if T[i-1] < T_c <= T[i] else 0

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

    # Finally, the derivative of the state. This calculates the derivative of all
    # nodes in the system - the nodes making up the tank, the collector, and the
    # aux heater. Used by the ODE solver.
    def Tdot(t, T, u):
        dT = zeros(T.shape)

        # Get current load and disturbance conditions.
        T_a = getAmbient(t)
        U_ins = getInsolation(t) / NC
        (m_load, T_load) = getLoad(t)

        # Even with 'internal control' we take a single-element input to tell
        # us when to heat.
        m_aux = m_aux_on * (1 if u[0] > 0.0001 else 0)
        if internalControl:
            U_aux = auxHeat(m_aux, t, T) * auxEfficiency / NX
            m_coll, m_coll_return = collPump(t, T)
        else:
            U_aux = u[1]
            m_coll, m_coll_return = u[2:4]

        # Calculate collector state change.
        for i in range(collFirst, collFirst+NC):
            U_amb = U_s_c * (T_a - T[i])
            if i is collFirst:
                U_mflow = m_coll        * C * (T[tankFirst] - T[i]) \
                        + m_coll_return * C * (T[collLast] - T[i])
            else:
                U_mflow = (m_coll + m_coll_return) * C * (T[i-1] - T[i])
            dT[i] = (U_amb + U_ins + U_mflow) / (rho * C * vC)

        # Calculate heater state change.
        for i in range(auxFirst, auxFirst+NX):
            U_amb = U_s_x * (T_a - T[i])
            if i is auxFirst:
                U_mflow = m_aux * C * (T[auxOutlet] - T[i])
            else:
                U_mflow = m_aux * C * (T[i-1] - T[i])
            dT[i] = (U_amb + U_aux + U_mflow) / (rho * C * vX)

        # The state changes in the tank depend on the temperatures of entering
        # water from the collector and aux heater, so let's make convenient
        # names for those:
        T_coll = T[collLast]
        T_aux = T[auxLast]

        # Convenience functions.
        Bl = lambda i: ctrlCold(T_load, T, i)
        Bc = lambda i: ctrlHot (T_coll, T, i)
        Bx = lambda i: ctrlHot (T_aux,  T, i)
        m  = lambda i: mflow(T, i, m_coll, m_load, m_aux, Bl, Bc, Bx)

        # Calculate tank state change.
        for i in range(tankFirst, tankFirst+NT):
            # Ambient temperature losses.
            # \todo{fix ends. Need to account for larger surface area there.}
            U_amb = U_s * (T_a - T[i])

            # Temperature flow from inlets. Use the B functions to only apply
            # these heat flows to the appropriate nodes.
            U_inlet = Bl(i) * m_load * C * (T_load - T[i]) \
                    + Bc(i) * m_coll * C * (T_coll - T[i]) \
                    + Bx(i) * m_aux  * C * (T_aux  - T[i])

            # Mass flow. Nodes will receive heat from the node above them, and
            # lose it to the node below them. The top and bottom tank nodes,
            # of course, only do one of these things.
            U_mflow = (min(0, m(i-1)) * C * (T[i] - T[i-1]) if i > 0 else 0) \
                    + (max(0, m(i))   * C * (T[i+1] - T[i]) if i < NT-1 else 0)

            # Final temperature change (\autoref{eq:node-dT})
            dT[i] = (U_amb + U_inlet + U_mflow) / (rho * C * vT)

        # Make the last internal control state available to external watchers.
        # This is used for analytics that need to know what flows are happening.
        Tdot.lastInternalControl = [m_aux, U_aux, m_coll, m_coll_return]
        return dT

    # Export this so it can be used externally.
    Tdot.internalController = auxPump
    return Tdot
