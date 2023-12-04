import casadi
import numpy as np
import matplotlib.pyplot as plt
import optimizer, functions, plot, forecasts

# ------------------------------------------------------
# Select problem type and solver
# ------------------------------------------------------

# Simulation time
num_iterations = 200

# Horizon
N = 25

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          N,
}

# Choose between solving the general case or a given combination of the deltas
general = False

# Print corresponding setup
plot.print_pb_type(pb_type)

# ------------------------------------------------------
# Initial state of the system
# ------------------------------------------------------

# Initial state
x_0 = [300.0]*4 + [320.0]*12

# Initial point around which to linearize
a = [330, 0.25] + [0.6]*4 + x_0

# ------------------------------------------------------
# Initialize variables for the final plot
# ------------------------------------------------------

list_Q_HP = []
list_S11, list_S21, list_S31, list_B4 = [x_0[4]], [x_0[8]], [x_0[12]], [x_0[3]]
delta_t_h = 2/60
elec_cost, elec_used = 0, 0

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

for iter in range(num_iterations):

    # Define the case to solve
    case = {'general': general, 'd_ch':0, 'd_bu':1, 'd_HP':1, 'd_R':0}
    
    # Get u* and x*
    u_opt, x_opt = optimizer.optimize_N_steps(x_0, a, iter, pb_type, case)
    
    # Extract u0* and x0
    u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
    x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]
    
    # Implement u_0* and obtain x_1
    x_1 = optimizer.dynamics(u_t=u_opt_0, x_t=x_0, a=a, real=True, approx=False)
    
    # Update x_0
    x_0 = x_1
    
    # Update "a", the point around which we linearize
    a = u_opt_0[:2] + [0.6]*4 + x_1

    # Print iteration
    plot.print_iteration(u_opt, x_opt, x_1, pb_type)
    
    # ------------------------------------------------------
    # Plots
    # ------------------------------------------------------

    # Update total electricity use and cost
    Q_HP = functions.get_function("Q_HP", u_opt_0, x_opt_0, 0, True, False)
    elec_used += Q_HP/4 * delta_t_h
    elec_cost += Q_HP/4 * delta_t_h * forecasts.get_c_el(iter,iter+1)[0]

    # Append values for the plot
    list_Q_HP.append(Q_HP)
    list_S11.append(x_1[4])
    list_S21.append(x_1[8])
    list_S31.append(x_1[12])
    list_B4.append(x_1[3])

# Regroup the data and send it to plot
plot_data = {
    'pb_type':      pb_type,
    'iterations':   num_iterations,
    'c_el':         forecasts.get_c_el(0,num_iterations),
    'm_load':       forecasts.get_m_load(0,num_iterations),
    'Q_HP':         list_Q_HP,
    'T_S11':        list_S11,
    'T_S21':        list_S21,
    'T_S31':        list_S31,
    'T_B4':         list_B4,
    'elec_cost':    round(elec_cost,2),
    'elec_used':    round(elec_used/1000,2),
}

print("\nPlotting the data...")
plot.plot_MPC(plot_data)