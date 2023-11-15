from linear_approx import f_id_y
import casadi
from sympy import symbols, diff, Symbol
import numpy as np

'''
This code provides an example of use for the f_id_y function.
- For a symbolic y, set example_symbolic to True
- For a real y, set example_symbolic to False
'''

# Choose between example types
example_symbolic = True

# ID of the function to approximate
id = 3

# Point around which to linearize
a_u = [310, 0.25, 0, 1, 0, 0]
a_x = [308]*4 + [313]*12

# Point at which to evaluate the function
# Example for a symbolic y
if example_symbolic:
    opti = casadi.Opti()
    x = opti.variable(16, 10+1)
    u = opti.variable(6, 10)
    y_u = u[:,0]
    y_x = x[:,0]
    real = False

# Point at which to evaluate the function
# Example for a real y:
else:
    y_u = [330,  0.25,   0,    1,    0,    0]
    y_x = [300]*4 + [323]*12
    real = True

# Estimate f_id(x) at y=(y_u,y_x) with linearization around a=(a_u,a_x)
f = f_id_y(id=id, a_u=a_u, a_x=a_x, y_u=y_u, y_x=y_x, real=real)
approx = f['approx']
exact = f['exact']
error = f['rel_error']

print("\ny = {}".format([y_u, y_x]))
print("a = {}\n".format([a_u, a_x]))
print("f_{}(y): {}\n".format(id,exact))
print("f_{}_a(y): {}\n".format(id,approx))
print("Relative error [%]: {}\n".format(error))
