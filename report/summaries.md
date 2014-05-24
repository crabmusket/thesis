# Summaries

## Grant08

### Introduction and final words

 * There are general convex program solvers and specialised ones that exploit
   aspects of problem definition or structure.
 * General solvers may be efficient in theory, but not in practise.
 * Specialised solvers require that the problem is transformed into some
   _standard form_ that they can solve.
 * Transformation may be obscure, difficult, and error-prone, even for experts.
 * Transformed problem may be larger (e.g. more constraints, free variables)
   but the solver may still be more efficient because of the problem structure.
 * These transformations are desirable and useful!
 * These transformations can be _automated_.
 * Experienced optimisation practitioners tend to construct programs from
   known convex functions ('atoms') and operations that combine them while
   preserving their convexity. Disciplined convex programming formalises this
   method.
 * Using graph methods, experts can implement automatic transformations of
   problems to standard form of many different solvers.
 * Non-expert and application-focused users are presented with an easy
   interface for expressing convex programs.
 * Separation of concerns.
 * "Closes the gap between convex optimisation theory and practise"

### DCP

 * Provides a ruleset for combining convex expressions.
 * Provides a 'library' of _atoms_ that are known to be convex.
 * Atoms are often expressed as extended-value equivalents of common functions.
   For example, `sqrt x | x < 0 = -∞`.
 * DCP requires users to provide "just enough structure" for the program to
   automatically transform it. For example, `sqrt . sum . square` is not valid
   due to DCP's function composition rules, even though it is numerically the
   same as the atom `norm`.
 * Therefore the DCP ruleset is sufficient for convexity, but not necessary
   (i.e. come convex expressions may not be valid DCP expressions).

### Graph implementations

 * A convex function has a convex epigraph, therefore finding the infimum of the
   epigraph solves the function. Thus atoms can be expressed as simple
   optimisation problems on the epigraph.
 * Same for concave functions with the hypograph.
 * Sub-problems are 'inlined' into the user's desired problem.
 * Introduces more variables and constraints, but the use of more efficient
   solvers. Tends to be beneficial in practise.
