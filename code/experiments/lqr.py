import matplotlib
matplotlib.use('agg')
from matplotlib.pyplot import * # Grab MATLAB plotting functions

from numpy import *             # Grab all of the NumPy functions
from numpy.linalg import *
from scipy.linalg import *
from control.matlab import *    # MATLAB-like functions

title('');
xlabel('Time (s)');
ylabel('Displacement (m)');

def makeProblem(N, m, k, c, *args):
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

    C = zeros((1, 2*N));
    C[0, N] = 1

    D = matrix(0);

    return (A, B, C, D)

def discretise(dt, (A, B, C, D)):
    Ad = matrix(expm2(A * dt))
    Bd = A.I * (Ad - eye(Ad.shape[0])) * B
    return (Ad, Bd, C, D)

## Define problem
# Number of masses
N = 5;
m = 0.1;
k = 1;
d = 0.01;

## LQR cost matrix
# Construct Q
Q_v = diag([1] + [2 for _ in range(N-2)] + [1]) \
    + diag(ones(N-1), -1) * -1 \
    + diag(ones(N-1), 1) * -1
Q = bmat([[k/2*Q_v,        zeros((N, N))], \
          [zeros((N, N)),  m/2*eye(N)]])

## LQR control
# Make systems
(A, B, C, D) = makeProblem(N, m, k, d, 'u')
(_, b, _, _) = makeProblem(N, m, k, d, 'w')

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

figure(1)
try:
    hold(True)
    plot(t2, r2)
    plot(t3, r3)
    savefig('lqr.png')
    hold(False)
except: pass
