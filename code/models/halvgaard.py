from numpy import array

def model(C, UA):
    A = array([[-UA/C]])
    Bu = array([[1/C]])
    Bw = 
    C = array([[1]])
    D = array([[0]])
    return (A, Bu, Bw, C, D)
