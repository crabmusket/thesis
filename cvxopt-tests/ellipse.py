import cvxopt
from cvxopt import matrix
from cvxpy import *

# Find the closest point along a line segment to an ellipse.
def ellipseToSegment(c, A, d, x1, x2):
	x1 = x1 - c
	x2 = x2 - c
	dx = x2 - x1
	n = c.shape[0]
	x = Variable(n)
	t = Variable(1)
	objective = Minimize(norm((x1 + t*dx) - x))
	constraints = [
		quad_form(x, A) <= 1,
		t >= 0,
		t <= 1,
	]
	return Problem(objective, constraints).solve()

c = matrix([0, 0], (2, 1))
A = matrix([1, 0, 0, 1], (2, 2))
x1 = matrix([2, 2], (2, 1))
x2 = matrix([-2, 2], (2, 1))

print ellipseToSegment(c, A, 1, x1, x2)
