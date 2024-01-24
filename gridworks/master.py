import casadi
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import optimizer, functions, plot, forecasts, sequencer

# ------------------------------------------------------
# Select problem type and solver
# ------------------------------------------------------

# Time step
delta_t_m = 4               # minutes
delta_t_h = delta_t_m/60    # hours
delta_t_s = delta_t_m*60    # seconds

# Horizon (8 hours)
N = int(8 * 1/delta_t_h)

# Simulation time (hours)
num_iterations = 24

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
# Initialize
# ------------------------------------------------------

# Initial state of the system (buffer + storage)
x_0 = [314.0, 314.6, 313.7, 308.8] + [310]*12

# Initial solver warm start
u_opt = np.zeros((6, N))
x_opt = np.zeros((16, N+1))

# Initial previous sequence
previous_sequence = {}
for i in range(8): previous_sequence[f'combi{i+1}'] = [1,1,1]

# Load previous sequence results from a csv file
file_path = input("\nResults file (enter to skip): ").replace(" ","")

# For the final plot
list_Q_HP = []
list_B1, list_B4, list_S11, list_S21, list_S31 = [x_0[0]], [x_0[3]], [x_0[4]], [x_0[8]], [x_0[12]]
elec_cost, elec_used = 0, 0

# Initial point around which to linearize
a = [330, 0.25] + [0.6]*4 + x_0

# ------------------------------------------------------
# MPC closed loop
# ------------------------------------------------------

start_time = time.time()

for iter in range(num_iterations):

    # ---------------------------------------------------
    # Forecasts
    # ---------------------------------------------------
    
    # Get the first hourly forecasts
    if iter==0:
        c_el = [round(x*1000*100,2) for x in forecasts.get_c_el(0, 24, 1)]
        m_load = forecasts.get_m_load(0, 24, 1)

    # Get next day forecasts at 4:00 PM - TODO: replace with real forecasts
    if iter%24==16:
        c_el = c_el + [x+1 for x in c_el[:24]]
        m_load = m_load + m_load[:24]
        
    # At the start of a new day, crop forecasts
    if iter%24==0:
        c_el = c_el[-24:]
        m_load = m_load[-24:]
     
    # To save the iteration in a csv file
    data = [{
        "T_B": [round(x,1) for x in x_0[:4]],
        "T_S": [round(x,1) for x in x_0[4:]],
        "iter": iter,
        "prices": c_el[iter%24:iter%24+8],
        "loads": m_load[iter%24:iter%24+8]
    }]

    # ---------------------------------------------------
    # Solver warm start
    # ---------------------------------------------------
    
    # Give the solver a warm start using the previous solution
    initial_x = [[float(x) for x in x_opt[k,-106:]] for k in range(16)]
    initial_u = [[float(u) for u in u_opt[k,-105:]] for k in range(6)]
    initial_x = np.array([initial_x_i+[0]*15 for initial_x_i in initial_x])
    initial_u = np.array([initial_u_i+[0]*15 for initial_u_i in initial_u])
    warm_start = {'initial_x': np.array(initial_x), 'initial_u': np.array(initial_u)}
    
    # ---------------------------------------------------
    # Find a sequence and solve the optimization problem
    # ---------------------------------------------------

    # Prepare package for possible long sequence check
    long_seq_pack = {'x_0': x_0, 'x_opt_prev': x_opt, 'u_opt_prev': u_opt}
    
    # As long as a feasible sequence is not found, try something new
    attempt = 1
    obj_opt = 1e5
    while obj_opt == 1e5:
        
        # Get a good sequence proposition (method depends on attempt)
        sequence = sequencer.get_sequence(c_el, m_load, iter, previous_sequence, file_path, attempt, long_seq_pack)
        
        # Try to solve the optimization problem, get u* and x*
        u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, a, 15*iter, pb_type, sequence, warm_start, True)
        
        # Next attempt
        attempt += 1
    
    # Save the working sequence for the next step
    sequencer.append_to_csv(data, sequence)
    previous_sequence = sequence
    
    # ---------------------------------------------------
    # Implement u0*, print/plot, and append results
    # ---------------------------------------------------
    
    # Extract u0* and x0
    u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
    x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]
    
    # Implement u_0* and obtain x_1
    x_1 = [float(x) for x in x_opt[:,15]]
        
    # Print iteration
    plot.print_iteration(u_opt, x_opt, x_1, pb_type, sequence, 15*iter)
    print(f"Cost of next 8 hours: {round(obj_opt,2)} $")
    elec_prices = [round(100*1000*x,2) for x in forecasts.get_c_el(15*iter, 15*iter+120, delta_t_h)]
    print([elec_prices[0], elec_prices[15], elec_prices[30], elec_prices[45],
    elec_prices[60], elec_prices[75], elec_prices[90], elec_prices[105]])
    
    # Plot the iteration
    plot_data = {
        'T_B1': [round(x,3) for x in x_opt[0,:]],
        'T_B4': [round(x,3) for x in x_opt[3,:]],
        'T_S11': [round(x,3) for x in x_opt[4,:]],
        'T_S21': [round(x,3) for x in x_opt[8,:]],
        'T_S31': [round(x,3) for x in x_opt[12,:]],
        'Q_HP': [functions.get_function("Q_HP", u_opt[:,t], x_opt[:,t], 0, True, False, t, sequence, 15*iter, delta_t_h) for t in range(120)],
        'c_el': [round(100*1000*x,2) for x in forecasts.get_c_el(iter*15, iter*15+120, delta_t_h)],
        'm_load': forecasts.get_m_load(iter*15, iter*15+120, delta_t_h),
        'sequence': sequence}
    #plot.plot_single_iter(plot_data)
    
    # Update x_0
    x_0 = x_1
    
    # Update "a", the point around which we linearize
    a = u_opt_0[:2] + [0.6]*4 + x_1
    
    # ------------------------------------------------------
    # Plots
    # ------------------------------------------------------

    # Update total electricity use and cost using the average Q_HP over 1h
    Q_HP = 0
    for k in range(15):
        Q_HP += functions.get_function("Q_HP", u_opt[:,k], x_opt[:,k], 0, True, False, 0, sequence, 15*iter, delta_t_h)
    Q_HP = Q_HP/15

    COP1, Q_HP_max = forecasts.get_T_OA(15*iter, 15*iter+1, delta_t_h)
    elec_used += Q_HP*COP1[0] * delta_t_h * 15
    elec_cost += Q_HP*COP1[0] * delta_t_h * 15 * forecasts.get_c_el(15*iter, 15*iter+1, delta_t_h)[0]

    # Append values for the plot
    list_B1.extend([round(float(x),6) for x in x_opt[0,0:15]])
    list_B4.extend([round(float(x),6) for x in x_opt[3,0:15]])
    list_S11.extend([round(float(x),6) for x in x_opt[4,0:15]])
    list_S21.extend([round(float(x),6) for x in x_opt[8,0:15]])
    list_S31.extend([round(float(x),6) for x in x_opt[12,0:15]])
    for k in range(15):
        list_Q_HP.append(functions.get_function("Q_HP", u_opt[:,k], x_opt[:,k], 0, True, False, 0, sequence, 15*iter, delta_t_h))

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

# Print total simulation time
total_time = time.time()-start_time
hours = round(total_time // 3600)
minutes = round((total_time % 3600) // 60)
print(f"The {num_iterations}-hour simulation ran in {hours} hour(s) and {minutes} minute(s).")
    
print("\nPlotting the data...\n")
plot.plot_MPC(plot_data)
