import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import casadi
import os

# ------------------------------------------
# Gather parameters
# ------------------------------------------

# The maximum storage capacity (kWh)
mass_of_water = 450*4 # 450kg water per tank
max_temp, min_temp = 65, 30 #°C
max_storage = mass_of_water * 4187 * (max_temp - min_temp) # in Joules
max_storage = round(max_storage * 2.77778e-7,1) # in kWh
print(f"The storage capacity is {max_storage} kWh.")

# Estimate Q_HP_max # TODO: replace with forecast.py
def Q_HP_max(T_OA):
    T_OA += 273
    B0_Q, B1_Q = -68851.589, 313.3151
    return round((B0_Q + B1_Q*T_OA)/1000,2) if T_OA<273-7 else 14
    
# Estimate 1/COP # TODO: replace with forecast.py
def COP1(T_OA):
    T_OA += 273
    B0_C, B1_C = 2.695868, -0.008533
    return round(B0_C + B1_C*T_OA,2)
    
# ------------------------------------------
# ------------------------------------------
# FIND THE OPTIMAL SEQUENCE
# ------------------------------------------
# ------------------------------------------

def get_optimal_sequence(iter, state):

    # ------------------------------------------
    # Get current forecasts
    # ------------------------------------------

    # Get current forecasts from iter
    load [kWh]
    c_el [cts/kWh]
    T_OA [°C]
    
    # Q_HP_max forecast from T_OA [kWh_th]
    Q_HP_max_list = [Q_HP_max(temp) for temp in T_OA]
    Q_HP_min_list = [8 for x in Q_HP_max_list]

    # 1/COP forecast from T_OA
    COP1_list = [COP1(temp) for temp in T_OA]

    # ------------------------------------------
    # Get current state, estimate storage, set as initial
    # ------------------------------------------

    # Average temperature of tanks
    T_avg = sum(state)/16
    current_storage = mass_of_water * 4187 * (T_avg - min_temp) * 2.77778e-7
    initial_storage = round(current_storage,1)

    # ------------------------------------------
    # Solve closed loop with initial storage
    # ------------------------------------------
    
    # Horizon
    N = 24

    # Get the solution from the optimization problem
    Q_opt, stor_opt, HP_on_off_opt, obj_opt = get_opti(N, c_el, load, max_storage, initial_storage, Q_HP_min_list, Q_HP_max_list, COP1_list)

    # Duplicate the last element of the hourly data for the plot
    c_el2 = c_el + [c_el[-1]]
    Q_opt2 = [round(x,3) for x in Q_opt] + [Q_opt[-1]]
    load2 = load + [load[-1]]

    # Plot
    fig, ax = plt.subplots(1,1, figsize=(13,5))
    ax.step(range(N+1), Q_opt2, where='post', label='Heat pump', alpha=0.4, color='blue')
    ax.plot(range(N+1), stor_opt, label='Storage', alpha=0.6, color='orange')
    ax.step(range(N+1), load2, where='post', label='Load', alpha=0.4, color='red')
    ax.step(range(N+1), [max_storage]*(N+1), where='post', color='orange', alpha=0.8, label='Maximum storage', linestyle='dotted')
    ax.step(range(N+1), Q_max2, where='post', color='blue', alpha=0.6, label='Maximum Q_HP', linestyle='dotted')
    ax.fill_between(range(N+1), load2, step="post", color='red', alpha=0.1)
    ax.fill_between(range(N+1), Q_opt2, step="post", color='blue', alpha=0.1)
    ax.set_xticks(range(N+1))
    ax.set_xlabel("Time [hours]")
    ax.set_ylabel("Energy [$kWh_{th}$]")
    plt.title(f"Cost: {obj_opt}$, Supplied: {round(sum(Q_opt2),1)} kWh_th")
    ax2 = ax.twinx()
    ax2.set_ylabel("Price [cts/kWh]")
    ax2.step(range(N+1), c_el2, where='post', label='Electricity price', color='black', alpha = 0.4)
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines2 + lines1, labels2 + labels1)
    plt.show()

    # ------------------------------------------
    # Return operating hours
    # ------------------------------------------
    
    return HP_on_off_opt










    


# ------------------------------------------
# Optimization problem
# ------------------------------------------

def get_opti(N, c_el, load, max_storage, storage_initial, Q_HP_min_list, Q_HP_max_list, COP1_list):

    # Initialize
    opti = casadi.Opti('conic')

    # -----------------------------
    # Variables and solver
    # -----------------------------

    storage = opti.variable(1,N+1)  # state
    Q_HP = opti.variable(1,N)       # input
    delta_HP = opti.variable(1,N)  # input
    Q_HP_onoff = opti.variable(1,N) # input (derived)

    # delta_HP is a discrete variable (binary)
    discrete_var = [0]*(N+1) + [0]*N + [1]*N + [0]*N

    # Solver
    opti.solver('gurobi', {'discrete':discrete_var, 'gurobi.OutputFlag':0})

    # -----------------------------
    # Constraints
    # -----------------------------

    # Initial storage level
    opti.subject_to(storage[0] == storage_initial)

    # Constraints at every time step
    for t in range(N+1):

        # Bounds on storage
        opti.subject_to(storage[t] >= 0)
        opti.subject_to(storage[t] <= max_storage)

        if t < N:
            
            # System dynamics
            opti.subject_to(storage[t+1] == storage[t] + Q_HP_onoff[t] - load[t])

            # Bounds on delta_HP
            opti.subject_to(delta_HP[t] >= 0)
            opti.subject_to(delta_HP[t] <= 1)
        
            # Bounds on Q_HP
            opti.subject_to(Q_HP[t] <= Q_HP_max_list[t])
            opti.subject_to(Q_HP[t] >= Q_HP_min_list[t]*delta_HP[t])
        
            # Bilinear to linear
            opti.subject_to(Q_HP_onoff[t] <= Q_HP_max_list[t]*delta_HP[t])
            opti.subject_to(Q_HP_onoff[t] >= Q_HP_min_list[t]*delta_HP[t])
            opti.subject_to(Q_HP_onoff[t] <= Q_HP[t] + Q_HP_min_list[t]*(delta_HP[t]-1))
            opti.subject_to(Q_HP_onoff[t] >= Q_HP[t] + Q_HP_max_list[t]*(delta_HP[t]-1))

    # -----------------------------
    # Objective
    # -----------------------------

    obj = sum(Q_HP_onoff[t]*c_el[t]*COP1_list[t] for t in range(N))
    opti.minimize(obj)

    # -----------------------------
    # Solve and get optimal values
    # -----------------------------

    sol = opti.solve()
    Q_opt = sol.value(Q_HP_onoff)
    stor_opt = sol.value(storage)
    HP_on_off_opt = sol.value(delta_HP)
    obj_opt = round(sol.value(obj)/100,2)

    return Q_opt, stor_opt, HP_on_off_opt, obj_opt
