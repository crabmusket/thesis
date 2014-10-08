from numpy import array

def model(C, UA, P, auxEfficiency):
    A  = array([[-UA/C]])
    Bu = array([[P * auxEfficiency / C]])
    Bw = array([[-60/C, 1/C, 1, UA/C]])
    C  = array([[1]])
    D  = array([[0]])
    return (A, Bu, Bw, C, D)
