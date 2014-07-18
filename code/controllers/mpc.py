from numpy import *
import numpy as np
from numpy.linalg import *
from scipy.linalg import *
from control.matlab import *

import cvxopt as cvx
from cvxpy import *

def discretise(dt, (A, Bu, Bd, C, D)):
    Adis = matrix(expm2(A * dt))
    B = np.hstack([Bu, Bd])
    Bdis = A.I * (Adis - eye(Adis.shape[0])) * B
    return (Adis,
            Bdis[:, 0           : Bu.shape[1]],
            Bdis[:, Bu.shape[1] : Bu.shape[1] + Bd.shape[1]],
            C, D)

# DSLs for the win!
def SubjectTo(*args):
    return [a for a in list(args) if a is not None]

def linear(H, dt, umax, sys, dist, *args):
    # Construct predictor from discretised SS model.
    (A, Bu, Bd, C, D) = discretise(dt, sys)
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
    b = builder(Bu)
    theta = bmat([[b(i, j) for j in range(0, H)] for i in range(0, H)])
    b = builder(Bd)
    theta_ = bmat([[b(i, j) for j in range(0, H)] for i in range(0, H)])
    psi = bmat([[C * matrix_power(A, i)] for i in range(1, H+1)])

    # Construct optimisation problem data.
    Theta  = cvx.matrix(theta)
    Theta_ = cvx.matrix(theta_)
    Psi    = cvx.matrix(psi)
    Q = cvx.matrix(kron(eye(H), diag([0]*(N-1) + [1] + [0]*N)))
    lastMask = cvx.matrix([0]*(H-1)*C.shape[0] + [1]*C.shape[0])

    def solve(x, t):
        if dist is not None:
            dists = [dist(tt, x) for tt in linspace(t, t+(H-1)*dt, H)]
            d = cvx.matrix(np.vstack(dists))
        else:
            d = cvx.matrix([0]*Bd.shape[1]*H)
        u = Variable(H * Bu.shape[1])
        y = Variable(H * C.shape[0])
        X = cvx.matrix(x)
        op = Problem(
            Minimize
                #(norm(y)), # Distances and velocities
                (quad_form(y, Q)), # Kinetic energy of system
                #(norm(Q*y, 1)), # Distance of last mass from 0
            SubjectTo
                (y == Psi * X + Theta * u + Theta_ * d,
                 #transpose(lastMask) * y == 0,
                 -umax <= u, u <= umax)
        )
        op.solve()
        if u.value is not None:
            return array(u.value)[0:Bu.shape[1], 0].reshape(Bu.shape[1], 1)
        else:
            raise Exception('Optimisation failed in state {}'.format(op.status))

    return solve
