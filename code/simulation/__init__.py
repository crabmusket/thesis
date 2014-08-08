from scipy.integrate import ode
from numpy import hstack, array

class Run(object):
    def __init__(self, xdot, x0, dt, tf, u = None):
        self.model = xdot
        self.x0 = x0
        self.tf = tf
        self.dt = dt
        self.u = u

    def result(self):
        t0 = 0
        sim = (ode(self.model)
                .set_integrator('zvode', method='bdf', with_jacobian=False)
                .set_initial_value(self.x0, t0))
        results = []
        inputs = []
        while sim.successful() and sim.t < self.tf:
            u = self.u(sim.y, sim.t) if self.u else array([0])
            sim.set_f_params(u)
            sim.integrate(sim.t + self.dt)
            results.append(sim.y)
            inputs.append(u)
        return (array(inputs).T, array(results).T)
