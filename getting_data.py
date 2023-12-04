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
iter = 0

# ------------------------------------------------------
# Get optimal cost of next N steps under given sequence
# ------------------------------------------------------

def one_iteration(x_0, iter, sequence, horizon):
    
    # Set the horizon
    pb_type['horizon'] = horizon
    
    # Get u* and x*
    u_opt, x_opt, obj_opt = optimizer.optimize_N_steps(x_0, 0, iter, pb_type, sequence)
    
    return round(obj_opt,3) #, x_opt, u_opt

# ------------------------------------------------------
# Allowed operating modes and Initial state
# ------------------------------------------------------

# The four possible modes
operating_modes = [[0,0,0], [0,1,0], [1,0,1], [1,1,1]]

# Initial state of the buffer and storage tanks
initial_state = [300.0]*4 + [320.0]*12
print(f"\nINITIAL STATE: \nBuffer: {initial_state[:4]} \nStorage: {initial_state[4:]}")

# Initialize
min_cost = 1000
optimals = []

# ------------------------------------------------------
# Find feasible combi1 over N=30min
# ------------------------------------------------------
#'''
if min_cost!=0:
    for combi1 in operating_modes:
        
        sequence = {'combi1': combi1}
        
        # Try one iteration at 30min horizon with combi 1
        cost = one_iteration(initial_state, iter, sequence, 15)
        print(f"\n******* combi1={combi1} *******\n")

        # If not feasible
        if cost == 1e5:
            print(f"combi1 = {combi1} is not feasible")
        
        # If feasible, check for associated feasible combi2
        else:
            print(f"combi1 = {combi1} has cost {cost} $. Testing for combi2:")
            
            # ------------------------------------------------------
            # Find feasible combi1, combi2 over N=1h
            # ------------------------------------------------------
            if min_cost!=0:
                for combi2 in operating_modes:
                
                    sequence = {'combi1': combi1, 'combi2': combi2}
                    cost = one_iteration(initial_state, iter, sequence, 30)
                    
                    if cost == 1e5:
                        print(f"- combi1={combi1}, combi2={combi2} is not feasible.")
                    
                    else:
                        print(f"- combi1={combi1}, combi2={combi2} has cost {cost} $. Testing for combi3:")
                        
                        # ------------------------------------------------------
                        # Find feasible combi1, combi2, combi3 over N=1h30
                        # ------------------------------------------------------
                        if min_cost!=0:
                            for combi3 in operating_modes:
                            
                                sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3}
                                cost = one_iteration(initial_state, iter, sequence, 45)
                                
                                if cost == 1e5:
                                    print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3} is not feasible.")
                                
                                else:
                                    print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3} has cost {cost} $. Testing for combi4:")
                                        
                                    # ------------------------------------------------------
                                    # Find feasible combi1, combi2, combi3, combi4 over N=2h
                                    # ------------------------------------------------------
                                    if min_cost!=0:
                                        for combi4 in operating_modes:
                                        
                                            sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4}
                                            cost = one_iteration(initial_state, iter, sequence, 60)
                                            
                                            if cost == 1e5:
                                                print(f"--- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} is not feasible.")
                                            
                                            else:
                                                print(f"--- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} has cost {cost} $. [ok]")
                                                
                                                # Compare to current minimum cost, update if better
                                                if cost < min_cost:
                                                    min_cost = cost
                                                    optimals = []
                                                    
                                                if cost == min_cost:
                                                    #optimals.append({'c1':combi1, 'c2':combi2, 'c3':combi3, 'c4':combi4})
                                                    optimals = [combi1, combi2, combi3, combi4]
                                                    
                                                if cost == 0.0:
                                                    print(f"\nCost = 0 for {combi1}, {combi2}, {combi3}, {combi4}\n")

print(min_cost)
print(optimals)
















'''
sequence = {'combi1': [1,1,1], 'combi2': [1,1,1], 'combi3': [1,1,1], 'combi4': [0,0,0]}
cost, x_opt, u_opt = one_iteration(initial_state, sequence, 60)
print("cost = ", cost)

print("\nInitial state:")
print([round(x,2) for x in x_opt[:,0]])

print("\n30min forward:")
print([round(x,2) for x in x_opt[:,15]])

print("\n1h forward:")
print([round(x,2) for x in x_opt[:,30]])

print("\n1h30min forward:")
print([round(x,2) for x in x_opt[:,45]])

print("\n2h forward:")
print([round(x,2) for x in x_opt[:,60]])

import plot, forecasts, functions
data = {
    'T_B1':  [round(x,3) for x in x_opt[0,:]],
    'T_B4':  [round(x,3) for x in x_opt[3,:]],
    'T_S11': [round(x,3) for x in x_opt[4,:]],
    'T_S21': [round(x,3) for x in x_opt[8,:]],
    'T_S31': [round(x,3) for x in x_opt[12,:]],
    'Q_HP': [functions.get_function("Q_HP", u_opt[:,t], x_opt[:,t], 0, True, False, t, sequence) for t in range(60)],
    'c_el': forecasts.get_c_el(0,60, 2/60),
    'm_load': forecasts.get_m_load(0,60, 2/60),
}
plot.plot_singe_iter(data)
'''
