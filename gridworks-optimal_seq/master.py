import numpy as np
import time
import optimizer, functions, plot, forecasts, sequencer

# ------------------------------------------------------
# Define problem type (time step, horizon, etc.)
# ------------------------------------------------------

# Time step
delta_t_m = 4               # minutes
delta_t_h = delta_t_m/60    # hours

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
plot.print_pb_type(pb_type, num_iterations)

# ------------------------------------------------------
# Initialize
# ------------------------------------------------------

# Initial state (buffer + storage)
x_0 = [310]*16

# Initial solver warm start
u_opt = np.zeros((6, N))
x_opt = np.zeros((16, N+1))

# Initial previous sequence
previous_sequence = {}
for i in range(8): previous_sequence[f'combi{i+1}'] = [1,1,1]

# Load previous sequence results from a csv file
file_path = input("\nResults file (enter to skip): ").replace(" ","")
if file_path=="": print("No file selected.")

# For the final plot
list_B1, list_B4 = [x_0[0]], [x_0[3]]
list_S11, list_S21, list_S31 = [x_0[4]], [x_0[8]], [x_0[12]]
list_Q_HP = []
elec_cost, elec_used = 0, 0

# Time the simulation
start_time = time.time()

# ------------------------------------------------------
# MPC closed loop
# ------------------------------------------------------

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
        c_el = c_el + c_el[:24]
        m_load = m_load + m_load[:24]
        
    # At the start of a new day, crop forecasts
    if iter%24==0:
        c_el = c_el[-24:]
        m_load = m_load[-24:]
        
    # At 2AM, sudden negative price
    # if iter==2: c_el[2] = -15
     
    # To save the iteration in a csv file
    csv_data = [{
        "T_B": [round(x,1) for x in x_0[:4]],
        "T_S": [round(x,1) for x in x_0[4:]],
        "iter": iter,
        "prices": c_el[iter%24:iter%24+8],
        "loads": m_load[iter%24:iter%24+8]
    }]

    # ---------------------------------------------------
    # Solver warm start from previous iteration
    # ---------------------------------------------------
    
    # The last 7 hours of the previous iteration
    initial_x = [[float(x) for x in x_opt[k,-106:]] for k in range(16)]
    initial_u = [[float(u) for u in u_opt[k,-105:]] for k in range(6)]
    
    # The last hour (hour 8) of this iteration is not initialized
    initial_x = np.array([initial_x_i+[0]*15 for initial_x_i in initial_x])
    initial_u = np.array([initial_u_i+[0]*15 for initial_u_i in initial_u])
    
    # Packed in a dict that is given to the solver
    warm_start = {'initial_x': np.array(initial_x), 'initial_u': np.array(initial_u)}
    
    # ---------------------------------------------------
    # Find a sequence and solve the optimization problem
    # ---------------------------------------------------

    # Prepare package for possible long sequence search function
    long_seq_pack = {'x_0': x_0, 'x_opt_prev': x_opt, 'u_opt_prev': u_opt}
    
    # As long as a feasible sequence is not found, try another method (attempt)
    attempt = 1
    obj_opt = 1e5
    while obj_opt == 1e5:
        
        # Get a good sequence proposition (method depends on attempt)
        sequence = sequencer.get_optimal_sequence(c_el, m_load, iter, previous_sequence, file_path, attempt, long_seq_pack)
        
        # Try to solve the optimization problem, get u* and x*
        u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, 15*iter, pb_type, sequence, warm_start, True)
        
        # Next attempt
        attempt += 1
    
    # Save the working sequence to compare at the next step
    previous_sequence = sequence
    
    # Save results in a csv file
    sequencer.append_to_csv(csv_data, sequence)
    
    # ---------------------------------------------------
    # Implement u0*, update x_0, print and plot iteration
    # ---------------------------------------------------
    
    # Implement u_0* and obtain x_1
    x_1 = [float(x) for x in x_opt[:,15]]
    
    # Update x_0
    x_0 = x_1
        
    # Print iteration
    plot.print_iteration(u_opt, x_opt, x_1, pb_type, sequence, 15*iter)
    print(f"Cost of next 8 hours: {round(obj_opt,2)} $")
    print(f"Prices in the next 8 hours: {[round(100*1000*x,2) for x in forecasts.get_c_el(iter,iter+8,1)]}")
    
    # Plot iteration
    plot_data = {
        'T_B1': [round(x,3) for x in x_opt[0,:]],
        'T_B4': [round(x,3) for x in x_opt[3,:]],
        'T_S11': [round(x,3) for x in x_opt[4,:]],
        'T_S21': [round(x,3) for x in x_opt[8,:]],
        'T_S31': [round(x,3) for x in x_opt[12,:]],
        'Q_HP': [functions.get_function("Q_HP", u_opt[:,t], x_opt[:,t], t, sequence, 15*iter, delta_t_h) for t in range(120)],
        'c_el': [round(100*1000*x,2) for x in forecasts.get_c_el(iter*15, iter*15+120, delta_t_h)],
        'm_load': forecasts.get_m_load(iter*15, iter*15+120, delta_t_h),
        'sequence': sequence}
    #plot.plot_single_iter(plot_data)
    
    # ------------------------------------------------------
    # Update and append values for final plot
    # ------------------------------------------------------

    # Update electricity use (kWh) and cost ($) with next hour
    Q_HP = sum([functions.get_function("Q_HP", u_opt[:,t], x_opt[:,t], t, sequence, 15*iter, delta_t_h) for t in range(15)])/15
    COP1, _ = forecasts.get_T_OA(15*iter, 15*iter+1, delta_t_h)
    elec_used += Q_HP*COP1[0]
    elec_cost += Q_HP*COP1[0] * forecasts.get_c_el(15*iter, 15*iter+1, delta_t_h)[0]

    # Append state and Q_HP values with next hour
    list_B1.extend([round(float(x),6) for x in x_opt[0,0:15]])
    list_B4.extend([round(float(x),6) for x in x_opt[3,0:15]])
    list_S11.extend([round(float(x),6) for x in x_opt[4,0:15]])
    list_S21.extend([round(float(x),6) for x in x_opt[8,0:15]])
    list_S31.extend([round(float(x),6) for x in x_opt[12,0:15]])
    list_Q_HP.extend([functions.get_function("Q_HP", u_opt[:,t], x_opt[:,t], 0, sequence, 15*iter, delta_t_h) for t in range(15)])

# ------------------------------------------------------
# Final prints and plot
# ------------------------------------------------------

# Regroup plot data
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
print(f"\nThe {num_iterations}-hour simulation ran in {hours} hour(s) and {minutes} minute(s).")
    
print("\nPlotting the data...\n")
plot.plot_MPC(plot_data)
