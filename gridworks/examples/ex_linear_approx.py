import casadi
from sympy import symbols, diff, Symbol
import numpy as np
from functions import get_function
import functions
import time

'''
This code provides an example of use for the f_id_y function.
- For a symbolic y, set example_symbolic to True
- For a real y, set example_symbolic to False
'''

# Choose between example types
example_symbolic = False

# ID of the function to approximate
id = "T_sup_load"

# Point around which to linearize
a = [310, 0.25, 0.5, 1, 1, 0] + [308]*4 + [313]*12
start_time = time.time()
a = {
'values': a,
'functions_a': functions.get_all_f(a),
'gradients_a': functions.get_all_grad_f(a)
}
print("\nTime for obtaining all f(a) and grad_f(a): ", time.time()-start_time)

# Point at which to evaluate the function
# Example for a symbolic y
if example_symbolic:
    opti = casadi.Opti()
    u = opti.variable(6, 10)
    x = opti.variable(16, 10+1)
    u = u[:,0]
    x = x[:,0]
    y = casadi.vertcat(u,x)
    real = False

# Point at which to evaluate the function
# Example for a real y
else:
    u = [330, 0.3, 0, 1, 1, 0]
    x = [300]*4 + [323]*12
    y = u + x
    real = True
    
# Estimate f(y) around "a", where y=(u,x)
start_time = time.time()
f = get_function(id, u, x, a, real, True)
print("Time for obtaining f_a(y): ", time.time()-start_time)
    
# Print the results
print("\ny = {}".format(y))
print("a = {}\n".format(a['values']))
print("{}_a(y): {}\n".format(id,f))
