import casadi
import numpy as np
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
num_iterations = 1#int(16 * 1/delta_t_h / 15)

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
#x_0 = [317.1, 315.7, 314.4, 313.9] + [308.8, 307.5, 306.7, 306.1, 305.8, 305.6, 305.4, 304.9, 304.0, 302.7, 301.3, 300.3]
#x_0 = [316.3, 315.1, 313.8, 313.0] + [308.8, 307.5, 306.7, 306.1, 305.8, 305.6, 305.4, 304.9, 304.0, 302.7, 301.3, 300.3]
#x_0 = [320.2, 319.7, 319.1, 318.3] + [309.4, 307.6, 306.7, 306.1, 305.8, 305.6, 305.4, 304.9, 304.0, 302.8, 301.4, 300.3]

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

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

for iter in range(num_iterations):

    # Predicted optimal sequence of combinations (d_ch, d_bu, d_HP)
    sequence = forecasts.get_optimal_sequence(x_0, 15*iter, x_opt, u_opt)
        
    # Get u* and x*
    u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, a, 15*iter, pb_type, sequence, True)
    
    # Extract u0* and x0
    u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
    x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]
    
    # Implement u_0* and obtain x_1
    x_1 = [round(float(x),6) for x in x_opt[:,15]]
        
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
    print(f"Average Q_HP = {round(Q_HP,2)}")
    print(f"Electricity price: {round(forecasts.get_c_el(15*iter, 15*iter+1, delta_t_h)[0]*100*1000,2)} cts/kWh")
    print(f"Step cost = {round(Q_HP/4 * delta_t_h * 15 * forecasts.get_c_el(15*iter, 15*iter+1, delta_t_h)[0],2)}")

    # Assume a constant COP of 4
    elec_used += Q_HP/4 * delta_t_h * 15
    elec_cost += Q_HP/4 * delta_t_h * 15 * forecasts.get_c_el(15*iter, 15*iter+1, delta_t_h)[0]

    # Append values for the plot
    list_Q_HP.append(Q_HP)
    list_B1.append(x_1[0])
    list_B4.append(x_1[3])
    list_S11.append(x_1[4])
    list_S21.append(x_1[8])
    list_S31.append(x_1[12])

# Regroup the data and send it to plot
plot_data = {
    'pb_type':      pb_type,
    'iterations':   num_iterations,
    'c_el':         forecasts.get_c_el(0, 15*num_iterations, 15*delta_t_h),
    'm_load':       forecasts.get_m_load(0, num_iterations, delta_t_h),
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
