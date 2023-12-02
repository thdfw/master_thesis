import casadi
import numpy as np
import matplotlib.pyplot as plt
import optimizer, functions, plot, forecasts

# Time step
delta_t_m = 2 # minutes

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          60,
'time_step':        delta_t_m,
}

# Print corresponding setup
plot.print_pb_type(pb_type)

# ------------------------------------------------------
# Get optimal cost of next N steps under given sequence
# ------------------------------------------------------

def one_iteration(x_0, sequence, horizon):
    
    # Set the horizon
    pb_type['horizon'] = horizon
    
    # Get u* and x*
    u_opt, x_opt, obj_opt = optimizer.optimize_N_steps(x_0, 0, 0, pb_type, sequence)
    
    print(f"Cost = {round(obj_opt,3)}")
    return round(obj_opt,3)

# ------------------------------------------------------
# Compare costs between different feasible combinations
# ------------------------------------------------------

initial_state = [300.0]*4 + [320.0]*12

try_sequence = {
'combi1': [0,1,1], #0h00-0h30
'combi2': [0,1,1], #0h30-1h00
'combi3': [0,1,1], #1h00-1h30
'combi4': [0,1,1], #1h30-2h00
}
cost = one_iteration(initial_state, try_sequence, 60)

try_sequence = {
'combi1': [0,1,0], #0h00-0h30
'combi2': [0,1,0], #0h30-1h00
'combi3': [0,1,1], #1h00-1h30
'combi4': [0,1,1], #1h30-2h00
}
cost = one_iteration(initial_state, try_sequence, 60)
