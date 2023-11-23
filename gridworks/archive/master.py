import casadi
import numpy as np
import matplotlib.pyplot as plt
import optimizer
import functions

# ------------------------------------------------------
# Select problem type and solver
# ------------------------------------------------------

# Simulation time
num_iterations = 4

# Horizon
N = 2

pb_type = {
'linearized':       True,
'mixed-integer':    True,
'gurobi':           True,
'horizon':          N
}

# ------------------------------------------------------
# Print
# ------------------------------------------------------

# Linearized or not
if pb_type['linearized']: print("\nProblem type: Linearized")
else: print("\nProblem type: Non-linear")

# Variables: mixed integer or continuous
if pb_type['mixed-integer']: print("Variables: Mixed-Integer")
else: print("Variables: Continuous")

# Solver: gurobi or ipopt
if pb_type['gurobi']: print("Solver: Gurobi")
else:
    print("Solver: Ipopt")
    if pb_type['mixed-integer']: raise ValueError("Change the solver to Gurobi to solve the MIP.")

# ------------------------------------------------------
# Initial state of the system
# ------------------------------------------------------

# Initial state
x_0 = [320.0]*4 + [325.0]*12

# Initial point around which to linearize
#   T_HP  m_stor  d_ch, d_bu, d_HP, d_R
a = [330, 0.25] + [0.6]*4 + x_0

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

for iter in range(num_iterations):

    # Get u_0*
    u_0_optimal = optimizer.optimize_N_steps(x_0, a, iter, pb_type)
    
    # Implement u_0* and obtain x_1
    x_1 = optimizer.dynamics(u_t=u_0_optimal, x_t=x_0, a=a, real=True, approx=False)
    
    # Update x_0
    x_0_old = x_0
    x_0 = x_1
    
    # Update "a", the point around which we linearize
    a = u_0_optimal[:2] + [0.6]*4 + x_1

    # ------------------------------------------------------
    # Prints
    # ------------------------------------------------------
    
    # Get rounded x0 and x1
    round_x0 = [round(x,2) for x in x_0_old]
    round_x1 = [round(x,2) for x in x_1]
    
    print("\nResults:")
    print("T_B = {}, T_S1 = {}, T_S2 = {}, T_S3 = {}".format(round_x0[:4], round_x0[4:8],round_x0[8:12], round_x0[12:]))
    print("u_0* = {}".format([round(x,2) for x in u_0_optimal]))
    print("T_B = {}, T_S1 = {}, T_S2 = {}, T_S3 = {}".format(round_x1[:4], round_x1[4:8],round_x1[8:12], round_x1[12:]))
    
    # ------------------------------------------------------
    # Plots
    # ------------------------------------------------------

    # Store data
    # Send data to plots.py
    
    ''' tests
    a_fake = {
    'values': a,
    'functions_a': functions.get_all_f(a),
    'gradients_a': functions.get_all_grad_f(a)
    }
    print("m_buffer real = ", functions.get_function("m_buffer", u_0_optimal, x_0_old, a_fake, True, False))
    print("m_buffer approx = ", functions.get_function("m_buffer", u_0_optimal, x_0_old, a_fake, True, True))
    '''
