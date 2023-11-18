import casadi
import numpy as np
import matplotlib.pyplot as plt
from get_linear_approx import f_approx
import get_exact
import optimizer
from optimizer import optimize_N_steps

# ------------------------------------------------------
# Select problem type and solver
# ------------------------------------------------------

# Simulation time
num_iterations = 3

# Horizon
N = 3

pb_type = {
'linearized':       True,
'mixed-integer':    True,
'gurobi':           True,
'horizon':          N
}

# ------------------------------------------------------
# Print
# ------------------------------------------------------

# Solver: gurobi or ipopt
if pb_type['gurobi']: print("\nSolver: Gurobi")
else: print("\nSolver: Ipopt")
    
# Variables: mixed integer or continuous
if pb_type['mixed-integer']: print("Variables: Mixed-Integer")
else: print("Variables: Continuous")
    
# Linearized or not
if pb_type['linearized']: print("Problem type: Linearized\n\nComputing linear approximations...\n")
else: print("Problem type: Non-linear\n")
    
# For mixed-integer, need to use Gurobi
if pb_type['mixed-integer'] and (not pb_type['gurobi']): raise ValueError("Change the solver to Gurobi to solve the MIP.")

# ------------------------------------------------------
# Initial state of the system
# ------------------------------------------------------

# Initial state
x_0 = [320]*16

# Initial point around which to linearize
a = [310, 0.25, 0, 1, 0, 0] + x_0

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

for iter in range(num_iterations):

    # Get u_0*
    u_0_optimal = optimize_N_steps(x_0, a, iter, pb_type)
    
    # Implement u_0* and obtain x_1
    x_1 = get_exact.x_1(u_0_optimal, x_0)

    # ------------------------------------------------------
    # Prints
    # ------------------------------------------------------
    
    # Print iteration and simulated time
    hours = int(iter*1/12)
    minutes = round((iter*1/12-int(iter*1/12))*60)
    print("\n-----------------------------------------------------")
    print("Iteration {} ({}h{}min)".format(iter+1, hours, minutes))
    print("-----------------------------------------------------\n")

    # Print state, u0*, next state
    print("x_0 = {}".format([round(x,2) for x in x_0]))
    print("u_0* = {}".format([round(x,2) for x in u_0_optimal]))
    print("x_1 = {}".format([round(x,2) for x in x_1]))
    
    # ------------------------------------------------------
    # Get ready for next step
    # ------------------------------------------------------
    
    # Update the value of x_0
    x_0 = x_1

    # Update the value of a
    a = u_0_optimal[:2] + [0,1,0,0] + x_1
