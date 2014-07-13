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

def law(H, dt, umax, sys):
    # Construct predictor from discretised SS model.
    (A, B, C, D) = discretise(dt, sys)

    # Construct the matrices that predict the state over the prediction horizon.
    z = zeros((C*A*B).shape)
    def builder(i, j):
        if j > i:
            return z
        else:
            return C * matrix_power(A, i-j) * B
    psi = bmat([[C * matrix_power(A, i)] for i in range(1, H+1)])
    theta = bmat([[builder(i, j) for j in range(0, H)] for i in range(0, H)])

    # Construct optimisation problem data.
    Psi   = cvx.matrix(psi)
    Theta = cvx.matrix(theta)
    Q     = cvx.matrix(identity(H))

    def solve(x, t):
        u = Variable(H)
        y = Variable(H)
        X0 = cvx.matrix(x)
        op = Problem(
            Minimize
                (norm(y)),
            SubjectTo
                (y == Psi * X0 + Theta * u,
                 -umax <= u, u <= umax)
        )
        op.solve()
        return array(u.value).transpose().tolist()[0][0]

    return solve
