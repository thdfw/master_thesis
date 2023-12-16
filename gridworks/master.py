import casadi
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import optimizer, functions, plot, forecasts

# ------------------------------------------------------
# Select problem type and solver
# ------------------------------------------------------

# Time step
delta_t_m = 2               # minutes
delta_t_h = delta_t_m/60    # hours
delta_t_s = delta_t_m*60    # seconds

# Horizon (2 hours)
N = int(2 * 1/delta_t_h)

# Simulation time (16 hours)
num_iterations = int(16 * 1/delta_t_h / 15)

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          N,
'time_step':        delta_t_m,
}

# Print corresponding setup
plot.print_pb_type(pb_type)
print(f"Simulation: {round(num_iterations*15*delta_t_h)} hours ({num_iterations} iterations)")

# ------------------------------------------------------
# Initial state of the system
# ------------------------------------------------------

# Initial state
x_0 = [300.0]*4 + [320.0]*12
x_0 = [314.0, 314.6, 313.7, 308.8] + [308.8, 307.5, 306.7, 306.1, 305.8, 305.6, 305.4, 304.9, 304.0, 302.7, 301.3, 300.3]

# Initial point around which to linearize
a = [330, 0.25] + [0.6]*4 + x_0

# Initial warm start
u_opt = np.zeros((6, N))
x_opt = np.zeros((16, N+1))

# ------------------------------------------------------
# Initialize variables for the final plot
# ------------------------------------------------------

list_Q_HP = []
list_S11, list_S21, list_S31, list_B1, list_B4 = [x_0[4]], [x_0[8]], [x_0[12]], [x_0[0]], [x_0[3]]
elec_cost, elec_used = 0, 0

file_path = input("Results file: ").replace(" ","")
if file_path != "": df = pd.read_csv(file_path)

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

for iter in range(num_iterations):

    # Predicted optimal sequence of combinations (d_ch, d_bu, d_HP)
    if file_path == "": sequence = forecasts.get_optimal_sequence(x_0, 15*iter, x_opt, u_opt)
    else:
        seq = df['sequence'][iter]
        combi1 = seq[2:9].split(",")
        combi2 = seq[13:20].split(",")
        combi3 = seq[24:31].split(",")
        combi4 = seq[35:42].split(",")
        combi1 = [int(combi1[0]), int(combi1[1]), int(combi1[2])]
        combi2 = [int(combi2[0]), int(combi2[1]), int(combi2[2])]
        combi3 = [int(combi3[0]), int(combi3[1]), int(combi3[2])]
        combi4 = [int(combi4[0]), int(combi4[1]), int(combi4[2])]
        sequence = {'combi1':combi1, 'combi2':combi2, 'combi3':combi3, 'combi4':combi4}
    
    # Give the solver a warm start using the previous solution
    initial_x = [[round(x,4) for x in x_opt[k,-46:]] for k in range(16)]
    initial_u = [[round(u,4) for u in u_opt[k,-45:]] for k in range(6)]
    initial_x = np.array([initial_x_i+[0]*15 for initial_x_i in initial_x])
    initial_u = np.array([initial_u_i+[0]*15 for initial_u_i in initial_u])
    warm_start = {'initial_x': np.array(initial_x), 'initial_u': np.array(initial_u)}
    
    # Get u* and x*
    u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, a, 15*iter, pb_type, sequence, warm_start, True)
    
    # Extract u0* and x0
    u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
    x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]
    
    # Implement u_0* and obtain x_1
    x_1 = [round(float(x),6) for x in x_opt[:,15]]
    '''plus tard changer pour x_opt[:,14]!!'''
        
    # Print iteration
    plot.print_iteration(u_opt, x_opt, x_1, pb_type, sequence)
    print(f"Cost of next 2 hours: {round(obj_opt,2)} $")
    
    # Update x_0
    x_0 = x_1
    
    # Update "a", the point around which we linearize
    a = u_opt_0[:2] + [0.6]*4 + x_1
    
    # ------------------------------------------------------
    # Plots
    # ------------------------------------------------------

    # Update total electricity use and cost using the average Q_HP over 30min
    Q_HP = 0
    for k in range(15):
        Q_HP += functions.get_function("Q_HP", u_opt[:,k], x_opt[:,k], 0, True, False, 0, sequence)
    Q_HP = Q_HP/15

    # Assume a constant COP of 4
    elec_used += Q_HP/4 * delta_t_h * 15
    elec_cost += Q_HP/4 * delta_t_h * 15 * forecasts.get_c_el(15*iter, 15*iter+1, delta_t_h)[0]

    # Append values for the plot
    list_B1.extend([round(float(x),6) for x in x_opt[0,0:15]])
    list_B4.extend([round(float(x),6) for x in x_opt[3,0:15]])
    list_S11.extend([round(float(x),6) for x in x_opt[4,0:15]])
    list_S21.extend([round(float(x),6) for x in x_opt[8,0:15]])
    list_S31.extend([round(float(x),6) for x in x_opt[12,0:15]])
    for k in range(15):
        list_Q_HP.append(functions.get_function("Q_HP", u_opt[:,k], x_opt[:,k], 0, True, False, 0, sequence))

# Regroup the data and send it to plot
plot_data = {
    'pb_type':      pb_type,
    'iterations':   num_iterations,
    'c_el':         forecasts.get_c_el(0, 15*num_iterations, delta_t_h),
    'm_load':       forecasts.get_m_load(0, 15*num_iterations, delta_t_h),
    'Q_HP':         list_Q_HP,
    'T_S11':        list_S11,
    'T_S21':        list_S21,
    'T_S31':        list_S31,
    'T_B1':         list_B1,
    'T_B4':         list_B4,
    'elec_cost':    round(elec_cost,2),
    'elec_used':    round(elec_used/1000,2),
}

print("\nPlotting the data...")
plot.plot_MPC(plot_data)
