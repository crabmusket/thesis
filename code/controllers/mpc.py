from numpy import *
from numpy.linalg import *
from scipy.linalg import *
from control.matlab import *

import cvxopt as cvx
from cvxpy import *

def discretise(dt, (A, B, C, D)):
    Ad = matrix(expm2(A * dt))
    Bd = A.I * (Ad - eye(Ad.shape[0])) * B
    return (Ad, Bd, C, D)

# DSLs for the win!
def SubjectTo(*args):
    return list(args)

def linear(H, dt, umax, sys, *args):
    # Construct predictor from discretised SS model.
    (A, B, C, D) = discretise(dt, sys)
    N = A.shape[0]/2

    # Construct the matrices that predict the state over the prediction horizon.
    z = zeros((C*A*B).shape)
    def builder(i, j):
        if j > i:
            return z
        else:
            return C * matrix_power(A, i-j) * B
    theta = bmat([[builder(i, j) for j in range(0, H)] for i in range(0, H)])
    psi = bmat([[C * matrix_power(A, i)] for i in range(1, H+1)])

    # Construct optimisation problem data.
    Theta = cvx.matrix(theta)
    Psi   = cvx.matrix(psi)
    Q     = cvx.matrix(kron(eye(H), diag([0]*(N-1) + [1] + [0]*N)))
    last  = cvx.matrix([0]*(H-1)*C.shape[0] + [1]*C.shape[0])

    def solve(x, t):
        u = Variable(H * B.shape[1])
        y = Variable(H * C.shape[0])
        X = cvx.matrix(x)
        op = Problem(
            Minimize
                #(norm(y, 1)), # Distances and velocities
                #(quad_form(y, Q)), # Kinetic energy of system
                (norm(Q*y, 1)), # Distance of last mass from 0
            SubjectTo
                (y == Psi * X + Theta * u,
                 #transpose(last) * y == 0,
                 -umax <= u,
                 u <= umax)
        )
        op.solve()
        return array(u.value)[0:B.shape[1], 0].reshape(B.shape[1], 1)

    return solve
