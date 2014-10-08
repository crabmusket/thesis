from numpy import *
import numpy as np
from numpy.linalg import *
from scipy.linalg import *
from control.matlab import *

import cvxopt as cvx
from cvxpy import *

# Implement discretisation according to \autoref{eq:discretise-xdot}.
def discretise(dt, (A, Bu, Bw, C, D)):
    Adis = array(expm2(A * dt))
    B = np.hstack([Bu, Bw])
    Bdis = inv(A) * (Adis - eye(Adis.shape[0])) * B
    return (Adis,
            Bdis[:, 0           : Bu.shape[1]],
            Bdis[:, Bu.shape[1] : Bu.shape[1] + Bw.shape[1]],
            C, D)

# DSLs for the win!
def SubjectTo(*args):
    return [a for a in list(args) if a is not None]

def LTI(horizon, step, system, objective, constraints, disturbances):
    H = horizon
    dt = step

    # Construct predictor from discretised SS model.
    (A, Bu, Bw, C, D) = discretise(dt, system)
    N = A.shape[0]/2

    # Construct the matrices that predict the state over the prediction horizon.
    def builder(B):
        z = zeros((C*A*B).shape)
        def inner(i, j):
            if j > i:
                return z
            else:
                return C * matrix_power(A, i-j) * B
        return inner

    # \Autoref{eq:mpc-theta-u}.
    b = builder(Bu)
    thetaU = bmat([[b(i, j) for j in range(0, H)] for i in range(0, H)])
    # \Autoref{eq:mpc-theta-d}.
    b = builder(Bw)
    thetaW = bmat([[b(i, j) for j in range(0, H)] for i in range(0, H)])
    # \Autoref{eq:mpc-psi}.
    psi = bmat([[C * matrix_power(A, i)] for i in range(1, H+1)])

    # Construct optimisation problem data.
    ThetaU = cvx.matrix(thetaU)
    ThetaW = cvx.matrix(thetaW)
    Psi    = cvx.matrix(psi)
    lastMask = cvx.matrix([0]*(H-1)*C.shape[0] + [1]*C.shape[0])

    def solve(t, x):
        if disturbances is not None:
            dists = [disturbances(tt, x) for tt in linspace(t, t+(H-1)*dt, H)]
            w = cvx.matrix(np.vstack(dists))
        else:
            w = cvx.matrix([0]*Bd.shape[1]*H)
        u = Variable(H * Bu.shape[1])
        y = Variable(H * C.shape[0])
        X = cvx.matrix(x)
        op = Problem(
            Minimize
                (objective(X, y)),
            SubjectTo
                (y == Psi * X + ThetaU * u + ThetaW * w) + \
                 constraints(X, y, u)
        )
        op.solve(solver=CVXOPT)
        if u.value is not None:
            return array(u.value)[0:Bu.shape[1]].flatten()
        else:
            raise Exception('Optimisation failed in state "{}"'.format(op.status))

    return solve

def controller(period, law, preprocess, pwm):
    def control(t, x):
        if t - control.lastTime >= period:
            control.lastTime = t
            control.lastSignal = law(t, preprocess(x))
            print t
        if pwm:
            switchOff = (t - control.lastTime) > (period * control.lastSignal)
            return array([0 if switchOff else 1])
        else:
            return control.lastSignal

    control.lastTime = -period
    return control
