from numpy import array

def model(C, UA, P,
        auxEfficiency, collEfficiency,
        collArea, sunAngleFactor):
    nuX = auxEfficiency
    nuC = collEfficiency
    A  = array([[-UA/C]])
    Bu = array([[P * nuX / C]])
    Bw = array([[-60/C, 1/C, nuC, UA/C]])
    C  = array([[1]])
    D  = array([[0]])
    return (A, Bu, Bw, C, D)
