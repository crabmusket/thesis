from numpy import matrix, diag, ones, zeros, eye, bmat

def model(N, m, k, c, **opts):
    a = diag(ones(N) * -2) \
      + diag(ones(N-1), 1) \
      + diag(ones(N-1), -1)
    A = bmat([[zeros((N, N)), eye(N)], [k/m*a, c/m*a]])

    if 'control' in opts:
        control = opts['control']
        inputs = len(control)
        B = matrix(zeros((2*N, inputs)))
        for i in range(inputs):
            B[control[i], i] = 1
    else:
        B = matrix(zeros((2*N, 1)))

    if 'observe' in opts:
        if opts['observe'] == 'all':
            C = eye(2*N)
        else:
            observe = opts['observe']
            obs = len(observe)
            C = zeros((obs, 2*N))
            for i in range(obs):
                C[i, observe[i]] = 1
    else:
        C = zeros((1, 2*N))

    D = matrix(0)

    return (A, B, C, D)
