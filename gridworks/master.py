import numpy as np
import time
import optimizer, functions, plot, forecasts, sequencer

# ------------------------------------------------------
# Define problem type (time step, horizon, etc.)
# ------------------------------------------------------

# Time step
delta_t_m = 4               # minutes
delta_t_h = delta_t_m/60    # hours

# Integration method (euler, rk2, or rk4)
integration_method = 'rk2'

# Horizon (hours * time_steps/hour)
N = int(2 * 1/delta_t_h)

# Simulation time (hours)
num_iterations = 2

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          N,
'time_step':        delta_t_m,
'integration':      integration_method,
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
print("No file selected.") if file_path=="" else print(f"Reading from {file_path.split('/')[-1]}.")

# For the final plot
list_B1, list_B2, list_B3, list_B4 = [[elem] for elem in x_0[:4]]
list_S11, list_S12, list_S13, list_S14 = [[elem] for elem in x_0[4:8]]
list_S21, list_S22, list_S23, list_S24 = [[elem] for elem in x_0[8:12]]
list_S31, list_S32, list_S33, list_S34 = [[elem] for elem in x_0[12:16]]
list_Q_HP = []
elec_cost, elec_used = 0, 0

# Time the simulation
start_time = time.time()

# ------------------------------------------------------
# MPC closed loop
# ------------------------------------------------------

for iter in range(num_iterations):

    # ---------------------------------------------------
    # Solver warm start from previous iteration
    # ---------------------------------------------------
    
    # The last N-1 hours of the previous iteration
    initial_x = [[float(x) for x in x_opt[k,-(15*(int(N*delta_t_h)-1))-1:]] for k in range(16)]
    initial_u = [[float(u) for u in u_opt[k,-(15*(int(N*delta_t_h)-1)):]] for k in range(6)]
    
    # The last hour of the current iteration is not initialized
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
    previous_attempt = 0
    while obj_opt == 1e5:
        
        # Get a good sequence proposition (method depends on attempt)
        sequence, prev_attempt = sequencer.get_optimal_sequence(iter, previous_sequence, previous_attempt, file_path, attempt, long_seq_pack, pb_type)
                
        # Try to solve the optimization problem, get u* and x*
        u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, 15*iter, pb_type, sequence, warm_start, True)
        
        # Next attempt
        attempt += 1
        previous_attempt = prev_attempt
    
    # Save the working sequence to compare at the next step
    previous_sequence = sequence
    
    # Save results in a csv file
    sequencer.append_to_csv(x_0, iter, sequence, pb_type)
    
    # ---------------------------------------------------
    # Implement u0*, update x_0, print and plot iteration
    # ---------------------------------------------------
    
    # Implement u_0* and obtain x_1
    x_1 = [float(x) for x in x_opt[:,15]]
    
    # Update x_0
    x_0 = x_1
        
    # Print iteration
    plot.print_iteration(u_opt, x_opt, x_1, sequence, 15*iter)
    
    # Plot iteration
    plot_data = {
        'T_B1': [round(x,3) for x in x_opt[0,:]],
        'T_B4': [round(x,3) for x in x_opt[3,:]],
        'T_S11': [round(x,3) for x in x_opt[4,:]],
        'T_S21': [round(x,3) for x in x_opt[8,:]],
        'T_S31': [round(x,3) for x in x_opt[12,:]],
        'Q_HP': [functions.get_function("Q_HP", u_opt[:,t], x_opt[:,t], t, sequence, 15*iter) for t in range(int(15*N*delta_t_h))],
        'c_el': [round(100*1000*x,2) for x in forecasts.get_c_el(iter*15, iter*15+120, delta_t_h)],
        'm_load': forecasts.get_m_load(iter*15, iter*15+120, delta_t_h),
        'sequence': sequence}
    #plot.plot_single_iter(plot_data)
    
    # ------------------------------------------------------
    # Update and append values for final plot
    # ------------------------------------------------------

    # Get the Q_HP at evey time step over the next hour
    Q_HP_ = [functions.get_function("Q_HP", u_opt[:,t], x_opt[:,t], t, previous_sequence, 15*iter) for t in range(15)]
    Q_HP_ = [x/15 for x in Q_HP_]
    
    # Find the COP at evey time step over the next hour
    T_OA_, _, __ = forecasts.get_T_OA(15*iter, 15*(iter+1), delta_t_h)
    COP_ = [forecasts.get_COP(T_OA_[t], u_opt[0,t]) for t in range(15)]

    # Get the electricty used and the cost of electricity over the next hour
    for k in range(15):
        elec_used += Q_HP_[k] / COP_[k]
        elec_cost += Q_HP_[k] / COP_[k] * forecasts.get_c_el(15*iter, 15*iter+1, delta_t_h)[0]

    # Append state and Q_HP values with next hour
    list_B1.extend([round(float(x),6) for x in x_opt[0,0:15]])
    list_B2.extend([round(float(x),6) for x in x_opt[1,0:15]])
    list_B3.extend([round(float(x),6) for x in x_opt[2,0:15]])
    list_B4.extend([round(float(x),6) for x in x_opt[3,0:15]])
    list_S11.extend([round(float(x),6) for x in x_opt[4,0:15]])
    list_S12.extend([round(float(x),6) for x in x_opt[5,0:15]])
    list_S13.extend([round(float(x),6) for x in x_opt[6,0:15]])
    list_S14.extend([round(float(x),6) for x in x_opt[7,0:15]])
    list_S21.extend([round(float(x),6) for x in x_opt[8,0:15]])
    list_S22.extend([round(float(x),6) for x in x_opt[9,0:15]])
    list_S23.extend([round(float(x),6) for x in x_opt[10,0:15]])
    list_S24.extend([round(float(x),6) for x in x_opt[11,0:15]])
    list_S31.extend([round(float(x),6) for x in x_opt[12,0:15]])
    list_S32.extend([round(float(x),6) for x in x_opt[13,0:15]])
    list_S33.extend([round(float(x),6) for x in x_opt[14,0:15]])
    list_S34.extend([round(float(x),6) for x in x_opt[15,0:15]])
    list_Q_HP.extend([functions.get_function("Q_HP", u_opt[:,t], x_opt[:,t], 0, sequence, 15*iter) for t in range(15)])

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
    'T_S12':        list_S12,
    'T_S13':        list_S13,
    'T_S14':        list_S14,
    'T_S21':        list_S21,
    'T_S22':        list_S22,
    'T_S23':        list_S23,
    'T_S24':        list_S24,
    'T_S31':        list_S31,
    'T_S32':        list_S32,
    'T_S33':        list_S33,
    'T_S34':        list_S34,
    'T_B1':         list_B1,
    'T_B2':         list_B2,
    'T_B3':         list_B3,
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
plot.plot_MPC(plot_data, False, True)
plot.plot_MPC(plot_data, False, False)
