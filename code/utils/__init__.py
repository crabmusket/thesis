from itertools import islice

def iterate(f, initial):
    current = initial
    while 1:
        yield current
        current = f(current)

def take(n, l):
    return list(islice(l, n))
