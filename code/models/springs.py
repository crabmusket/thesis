from numpy import matrix, diag, ones, zeros, eye, bmat

def model(N, m, k, c, *args):
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

    if 'obsall' in args:
        C = eye(2*N)
    else:
        C = zeros((1, 2*N))
        C[0, N-1] = 1

    D = matrix(0)

    return (A, B, C, D)
