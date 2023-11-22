import casadi
import numpy as np
import matplotlib.pyplot as plt
import optimizer, functions, plot, forecasts

# ------------------------------------------------------
# Select problem type and solver
# ------------------------------------------------------

# Simulation time
num_iterations = 150

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

# Initial point around which to linearize
a = [330, 0.25] + [0.6]*4 + x_0

# For plots
list_Q_HP = []
list_S11, list_S21, list_S31 = [x_0[4]], [x_0[8]], [x_0[12]]

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

for iter in range(num_iterations):

    # Get u* and x*
    u_opt, x_opt = optimizer.optimize_N_steps(x_0, a, iter, pb_type)
    u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
    x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]

    # Implement u_0* and obtain x_1
    x_1 = optimizer.dynamics(u_t=u_opt_0, x_t=x_0, a=a, real=True, approx=False)
    
    # Update x_0
    x_0 = x_1
    
    # Update "a", the point around which we linearize
    a = u_opt_0[:2] + [0.6]*4 + x_1

    # ------------------------------------------------------
    # Prints
    # ------------------------------------------------------
    
    S_t = "->" if round(u_opt_0[2])==0 else "<-"
    S_b = "<-" if round(u_opt_0[2])==0 else "->"
    B_t = "->" if round(u_opt_0[3])==1 else "<-"
    B_b = "<-" if round(u_opt_0[3])==1 else "->"

    print(f"\nBuffer {B_t} {round(x_opt[0,0],1)} | Storage  {round(x_opt[12,0],1)} {S_t}    {round(x_opt[8,0],1)} {S_t}   {round(x_opt[4,0],0)} {S_t}")
    print(f"          {round(x_opt[1,0],1)} |          {round(x_opt[13,0],1)}       {round(x_opt[9,0],1)}      {round(x_opt[5,0],0)}")
    print(f"          {round(x_opt[2,0],1)} |          {round(x_opt[14,0],1)}       {round(x_opt[10,0],1)}      {round(x_opt[6,0],0)}")
    print(f"       {B_b} {round(x_opt[3,0],1)} |       {S_t} {round(x_opt[15,0],1)}    {S_t} {round(x_opt[11,0],1)}   {S_t} {round(x_opt[7,0],0)}\n")
        
    print(f"T_HP = {round(u_opt[0,0],1) if u_opt[4,0]==1 else '-'}, m_stor = {round(u_opt[1,0],1)}")
        
    print(f"\nBuffer {B_t} {round(x_1[0],1)} | Storage  {round(x_1[12],1)} {S_t}    {round(x_1[8],1)} {S_t}   {round(x_1[4],0)} {S_t}")
    print(f"          {round(x_1[1],1)} |          {round(x_1[13],1)}       {round(x_1[9],1)}      {round(x_1[5],0)}")
    print(f"          {round(x_1[2],1)} |          {round(x_1[14],1)}       {round(x_1[10],1)}      {round(x_1[6],0)}")
    print(f"       {B_b} {round(x_1[3],1)} |       {S_t} {round(x_1[15],1)}    {S_t} {round(x_1[11],1)}   {S_t} {round(x_1[7],0)}")
    
    # ------------------------------------------------------
    # Plots
    # ------------------------------------------------------

    # Store data
    list_Q_HP.append(functions.get_function("Q_HP", u_opt_0, x_opt_0, 0, True, False))
    list_S11.append(x_1[4])
    list_S21.append(x_1[8])
    list_S31.append(x_1[12])

# Send data to plots.py
plot_data = {
'iterations': num_iterations,
'c_el': forecasts.get_c_el(0,num_iterations),
'Q_load': forecasts.get_c_el(0,num_iterations),
'Q_HP': list_Q_HP,
'T_S11': list_S11,
'T_S21': list_S21,
'T_S31': list_S31,
}

print("\nPlotting the data...")
plot.plot_MPC(plot_data)
