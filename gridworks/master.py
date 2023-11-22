import casadi
import numpy as np
import matplotlib.pyplot as plt
import optimizer
import functions

# ------------------------------------------------------
# Select problem type and solver
# ------------------------------------------------------

# Simulation time
num_iterations = 35

# Horizon
N = 10

pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
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
x_0 = [300.0]*4 + [320.0]*12

# Initial point around which to linearize (deltas don't matter)
a = [330, 0.25] + [0]*4 + x_0

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

for iter in range(num_iterations):

    # Get u_0*
    u_optimal, x_optimal = optimizer.optimize_N_steps(x_0, a, iter, pb_type)
    u_0_optimal = [round(float(x),6) for x in u_optimal[:,0]]
    
    # Implement u_0* and obtain x_1
    x_1 = optimizer.dynamics(u_t=u_0_optimal, x_t=x_0, a=a, real=True, approx=False)
    
    # Update x_0
    x_0_old = x_0
    x_0 = x_1
    
    # Update "a", the point around which we linearize
    a = u_0_optimal[:2] + [0]*4 + x_1

    # ------------------------------------------------------
    # Prints
    # ------------------------------------------------------
    
    S_t = "->" if round(u_0_optimal[2])==0 else "<-"
    S_b = "<-" if round(u_0_optimal[2])==0 else "->"
    B_t = "->" if round(u_0_optimal[3])==1 else "<-"
    B_b = "<-" if round(u_0_optimal[3])==1 else "->"

    print(f"\nBuffer {B_t} {round(x_optimal[0,0],1)} | Storage  {round(x_optimal[12,0],1)} {S_t}    {round(x_optimal[8,0],1)} {S_t}   {round(x_optimal[4,0],0)} ->")
    print(f"          {round(x_optimal[1,0],1)} |          {round(x_optimal[13,0],1)}       {round(x_optimal[9,0],1)}      {round(x_optimal[5,0],0)}")
    print(f"          {round(x_optimal[2,0],1)} |          {round(x_optimal[14,0],1)}       {round(x_optimal[10,0],1)}      {round(x_optimal[6,0],0)}")
    print(f"       {B_b} {round(x_optimal[3,0],1)} |       {S_t} {round(x_optimal[15,0],1)}    {S_t} {round(x_optimal[11,0],1)}   {S_t} {round(x_optimal[7,0],0)}\n")
        
    print(f"T_HP = {round(u_optimal[0,0],1)}, m_stor = {round(u_optimal[1,0],1)}")
        
    print(f"\nBuffer {B_t} {round(x_1[0],1)} | Storage  {round(x_1[12],1)} {S_t}    {round(x_1[8],1)} {S_t}   {round(x_1[4],0)} {S_t}")
    print(f"          {round(x_1[1],1)} |          {round(x_1[13],1)}       {round(x_1[9],1)}      {round(x_1[5],0)}")
    print(f"          {round(x_1[2],1)} |          {round(x_1[14],1)}       {round(x_1[10],1)}      {round(x_1[6],0)}")
    print(f"       {B_b} {round(x_1[3],1)} |       {S_t} {round(x_1[15],1)}    {S_t} {round(x_1[11],1)}   {S_t} {round(x_1[7],0)}\n")
    
    # ------------------------------------------------------
    # Plots
    # ------------------------------------------------------

    # Store data
    # Send data to plots.py
    
    a_fake = {
    'values': a,
    'functions_a': 3,
    'gradients_a': 4
    }
    #print("T_sup_load real = ", functions.get_function("T_sup_load", u_0_optimal, x_0_old, a_fake, True, False))
    #print("m_buffer approx = ", functions.get_function("m_buffer", u_0_optimal, x_0_old, a_fake, True, True))
    
