from numpy import array

def model(m, C, UA, P, auxEfficiency):
    A  = array([[-UA/m/C]])
    Bu = array([[P/m/C * auxEfficiency]])
    Bw = array([[-50/m, 1/m, 1/m/C, UA/m/C]])
    C  = array([[1]])
    D  = array([[0]])
    return (A, Bu, Bw, C, D)
