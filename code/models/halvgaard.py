from numpy import array

#TODO LOL
def model(C, UA, NC):
    A  = array([[-UA/C]])
    Bu = array([[1/C]])
    Bw = array([1/C, -1/C, UA/C])
    C  = array([[1]])
    D  = array([[0]])
    return (A, Bu, Bw, C, D)
