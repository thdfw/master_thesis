import casadi
import numpy as np
import matplotlib.pyplot as plt
from linear_approx import f_id_y

# ------------------------------------------------------
# Variables
# ------------------------------------------------------

# Horizon x = x_0,...,x_N
N = 6

# Initialize CasADi
opti = casadi.Opti('conic')

# Define state and input variables
u = opti.variable(6, N)     # T_sup_HP, m_stor, d_ch, d_bu, d_HP, d_R
x = opti.variable(16, N+1)  # T_B1,...,T_B4, T_S11,...,T_S14, T_S21,...,T_S24, T_S31,...,T_S34

# All variables are continuous except d_ch, d_bu and d_HP (binary)
discrete_var = ([0]*2 + [1]*3 + [0]) * N
discrete_var += [0] * 16 * (N+1)
solver_opts = {'discrete': discrete_var, 'gurobi.OutputFlag': 0}
solver_opts = {'gurobi.OutputFlag': 0}

# ------------------------------------------------------
# Constraints
# ------------------------------------------------------

# Bounds constraints for u
for t in range(N):

    # T_sup_HP
    opti.subject_to(u[0,t] <= 273+65)
    opti.subject_to(u[0,t] >= 273+30)
    
    # m_stor
    opti.subject_to(u[1,t] <= 0.5)
    opti.subject_to(u[1,t] >= 0)
    
    # delta terms
    for i in range(2,6):
        opti.subject_to(u[i,t] >= 0)
        opti.subject_to(u[i,t] <= 1)

# Bounds constraints for x
for t in range(N+1):
    for i in range(16):
        opti.subject_to(x[i,t] >= 0)
        opti.subject_to(x[i,t] <= 1)
    
# ------------------------------------------------------
# Objective
# ------------------------------------------------------

# Linearize around a
a_u = [310, 0.25, 0, 1, 0, 0]
a_x = [308]*4 + [313]*12
id = 2

obj = sum(f_id_y(id=id, a_u=a_u, a_x=a_x, y_u=u[:,t], y_x=x[:,t], real=False)['approx'] for t in range(N))
opti.minimize(obj)

# ------------------------------------------------------
# Solving
# ------------------------------------------------------

# Solving the optimisation problem
opti.solver('gurobi', solver_opts)
sol = opti.solve()

# Get optimal u and x
u_optimal = sol.value(u)
x_optimal = sol.value(x)

# Print state, u0*, next state
print("")
print("Function to minimize:\n{}".format(f_id_y(id=id, a_u=a_u, a_x=a_x, y_u=u[:,0], y_x=x[:,0], real=False)['approx_readable']))
print("")
print("x_0 = {}".format([round(x,2) for x in x_optimal[:,0]]))
print("u_0* = {}".format([round(x,2) for x in u_optimal[:,0]]))
print("x_1 = {}".format([round(x,2) for x in x_optimal[:,1]]))
print("")
