from cvxopt import matrix
from cvxpy import *

# Find the closest point along a line segment to an ellipse.
def ellipseToSegment(c, A, d, x1, x2):
	# Transform to ellipse origin.
	x1 = x1 - c
	x2 = x2 - c
	dx = x2 - x1
	n = len(c)

	# Minimise the distance between a point on the line and a point on the
	# ellipse. Parameterise the line by t to stay on the segment.
	x = Variable(n)
	t = Variable(1)
	op = Problem(
		Minimize(norm((x1 + t*dx) - x)), [
		quad_form(x, A) <= 1,
		t >= 0,
		t <= 1,
	])
	op.solve()

	# Check distance plus floating-point epsilon.
	return op.objective.value <= d + 0.000001

c = matrix([0, 0], (2, 1))
A = matrix([1, 0, 0, 1], (2, 2))
x1 = matrix([2, 2], (2, 1))
x2 = matrix([-2, 2], (2, 1))
print ellipseToSegment(c, A, 1, x1, x2)

c = matrix([1, 1], (2, 1))
A = matrix([1, 0, 0, 5], (2, 2))
x1 = matrix([0, 1], (2, 1))
x2 = matrix([0, -1], (2, 1))
print ellipseToSegment(c, A, 0, x1, x2)
