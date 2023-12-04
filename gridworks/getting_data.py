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
# plot.print_pb_type(pb_type)

# ------------------------------------------------------
# Get optimal cost of next N steps under given sequence
# ------------------------------------------------------

def one_iteration(x_0, sequence, horizon):
    
    # Set the horizon
    pb_type['horizon'] = horizon
    
    # Get u* and x*
    u_opt, x_opt, obj_opt = optimizer.optimize_N_steps(x_0, 0, 0, pb_type, sequence)
    
    return round(obj_opt,3)

# ------------------------------------------------------
# Allowed operating modes and Initial state
# ------------------------------------------------------

# The four possible modes
operating_modes = [[0,0,0], [0,1,0], [1,0,1], [1,1,1]]
translation = {
    '[0,0,0]': "HP off, Storage discharging, buffer charging",
    '[0,1,0]': "HP off, Storage discharging, buffer discharging",
    '[1,0,1]': "HP on, Storage discharging, buffer charging",
    '[1,1,1]': "HP on, Storage discharging, buffer discharging",
}

# Initial state of the buffer and storage tanks
initial_state = [310.0]*4 + [300.0]*12
print(f"\nINITIAL STATE: \nBuffer: {initial_state[:4]} \nStorage: {initial_state[4:]}")

# ------------------------------------------------------
# Get feasible combi1
# ------------------------------------------------------

feasible_combi1 = []
feasible_combi2 = []
feasible_combi3 = []
optimals = []
min_cost = 1000
feasible_combi12 = {}

if min_cost!=0:
    for combi1 in operating_modes:
        
        sequence = {'combi1': combi1}
        
        # Try one iteration at 30min horizon with possible combi 1
        cost = one_iteration(initial_state, sequence, 15)
        print(f"\n******* combi1={combi1} *******\n")

        # If combi1 is not feasible
        if cost == 1e5:
            print(f"combi1 = {combi1} is not feasible")
        
        # If feasible, check for associated feasible combi2
        else:
            print(f"combi1 = {combi1} has cost {cost} $. Testing for combi2:")
            feasible_combi1.append(combi1)
            
            # ------------------------------------------------------
            # Find corresponding feasible combi2
            # ------------------------------------------------------
            if min_cost!=0:
                for combi2 in operating_modes:
                
                    sequence = {'combi1': combi1, 'combi2': combi2}
                    cost = one_iteration(initial_state, sequence, 30)
                    
                    if cost == 1e5:
                        print(f"- combi1={combi1}, combi2={combi2} is not feasible.")
                    
                    else:
                        print(f"- combi1={combi1}, combi2={combi2} has cost {cost} $. Testing for combi3:")
                        
                        # ------------------------------------------------------
                        # Find corresponding feasible combi3
                        # ------------------------------------------------------
                        if min_cost!=0:
                            for combi3 in operating_modes:
                            
                                sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3}
                                cost = one_iteration(initial_state, sequence, 45)
                                
                                if cost == 1e5:
                                    print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3} is not feasible.")
                                
                                else:
                                    print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3} has cost {cost} $. Testing for combi4:")
                                        
                                    # ------------------------------------------------------
                                    # Find corresponding feasible combi4
                                    # ------------------------------------------------------
                                    if min_cost!=0:
                                        for combi4 in operating_modes:
                                        
                                            sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4}
                                            cost = one_iteration(initial_state, sequence, 60)
                                            
                                            if cost == 1e5:
                                                print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} is not feasible.")
                                            
                                            else:
                                                print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} has cost {cost} $.")
                                                
                                                if cost < min_cost:
                                                    min_cost = cost
                                                    optimals = []
                                                    
                                                if cost == min_cost:
                                                    optimals.append({'c1':combi1, 'c2':combi2, 'c3':combi3, 'c4':combi4})
                                                    
                                                if cost == 0.0:
                                                    print(f"\nCost = 0 for {'c1':combi1, 'c2':combi2, 'c3':combi3, 'c4':combi4}\n")

print(min_cost)
print(optimals)
