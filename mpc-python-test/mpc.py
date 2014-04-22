from numpy import *             # Grab all of the NumPy functions
from numpy.linalg import *
from matplotlib.pyplot import * # Grab MATLAB plotting functions
from control.matlab import *    # MATLAB-like functions

# If dt <= 0, gives the state space equations for xdot(x). Otherwise gives the
# equation for x(t+dt|x).
def makeProblem(N, m, k, c, dt, *args):
    a = diag(ones(N) * -2) \
      + diag(ones(N-1), 1) \
      + diag(ones(N-1), -1)
    A = bmat([[zeros((N, N)), eye(N)], [k/m*a, c/m*a]])

    if 'u' in args and 'w' in args:
        B = zeros((2*N, 2))
        B[N, 0] = 1
        B[2*N-1, 1] = 1
    else:
        B = zeros((2*N, 1))
        if 'w' in args:
            B[2*N-1, 0] = 1
        else:
            B[N, 0] = 1

    if dt > 0:
        A = A * dt + eye(A.shape[0])
        B = B * dt;

    C = zeros((1, 2*N));
    C[0, N] = 1

    D = 0;

    return (A, B, C, D)

## Define problem
# Number of masses
N = 3;
m = 0.1;
k = 1;
d = 0.01;

## LQR cost matrix
# Construct Q
Q_v = diag([1] + ones(N-2)*2 + [1]) \
    + diag(ones(N-1), -1) * -1 \
    + diag(ones(N-1), 1) * -1
Q = bmat([[k/2*Q_v,        zeros((N, N))], \
            [zeros((N, N)),  m/2*eye(N)]])

## LQR control
# Make systems
(A, B, C, D) = makeProblem(N, m, k, d, 0, 'u')
(_, b, _, _) = makeProblem(N, m, k, d, 0, 'w')

# rho = 10
(K, _, _) = lqr(A, B, Q, 10)
s2 = ss(A-B*K, b, C, D)

# rho = 0.1
(K, _, _) = lqr(A, B, Q, 0.1);
s3 = ss(A-B*K, b, C, D);

## Plot LQR
# Impulse responses
ts = linspace(0, 30, 500)
(r2, t2) = impulse(s2, T=ts)
(r3, t3) = impulse(s3, T=ts)
title('');
xlabel('Time (s)');
ylabel('Displacement (m)');
#hold(True); plot(t2, r2); plot(t3, r3); show(); hold(False)

## MPC
dt = 0.05
H = 50

# Do a proper simulation over the time horizon
(A, B, C, D) = makeProblem(N, m, k, d, 0, 'u');
s = ss(A, B, C, D)
(r, t) = step(s, T=linspace(0, H*dt, 200))

# Construct predictor from discretised SS model
(A, B, C, D) = makeProblem(N, m, k, d, dt, 'u');
z = zeros((C*A*B).shape)
def builder(i, j):
    if j > i:
        return z
    else:
        return C * matrix_power(A, i-j) * B
Psi = bmat([[C * matrix_power(A, i)] for i in range(1, H+1)])
Theta = bmat([[builder(i, j) for j in range(1, H+1)] for i in range(1, H+1)])

X0 = zeros((2*N, 1))
us = ones((H, 1))
ys = Psi * X0 + Theta * us
hold(True); plot(t, r); plot(linspace(dt, H*dt, H), ys); show(); hold(False)
