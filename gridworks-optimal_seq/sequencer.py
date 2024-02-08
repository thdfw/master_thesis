import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import casadi
import os
import forecasts

# ------------------------------------------
# ------------------------------------------
# Gather parameters
# ------------------------------------------
# ------------------------------------------

# The maximum storage capacity (kWh)
mass_of_water = 450*3 # 450kg water per tank
max_temp, min_temp = 65, 35 #°C
max_storage = mass_of_water * 4187 * (max_temp - min_temp) # in Joules
max_storage = round(max_storage * 2.77778e-7,1) # in kWh

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
# MINLP optimization problem
# ------------------------------------------
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

    
# ------------------------------------------
# ------------------------------------------
# FIND THE OPTIMAL SEQUENCE
# ------------------------------------------
# ------------------------------------------

def get_optimal_sequence(c_el, m_load, iter, previous_sequence, results_file, attempt, long_seq_pack):

    # --------------------------------------------
    # If previous results were given (csv file)
    # --------------------------------------------
    
    if results_file != "":
    
        # Read the csv as a pandas dataframe
        df = pd.read_csv(results_file)
        
        if iter < len(df):
    
            # Read the corresponding sequence in the file
            sequence_string = df['sequence'][iter]
            sequence_file_dict = {}
            for i in range(1,9):
                combi = sequence_string[2+(i-1)*11:9+(i-1)*11].split(",")
                sequence_file_dict[f'combi{i}'] = [int(combi[0]), int(combi[1]), int(combi[2])]
            
            return sequence_file_dict
    
    # ------------------------------------------
    # Get current forecasts
    # ------------------------------------------
    
    # Horizon and time step
    N = 8
    delta_t_h = 4/60
    
    # Price
    c_el = [round(x*1000*100,2) for x in forecasts.get_c_el(iter, iter+N, 1)]
    print(f"\nc_el = {c_el}")

    # Load
    cp, Delta_T_load = 4187,  5/9*20
    m_load = forecasts.get_m_load(iter, iter+N, 1)
    load = [round((m*cp*Delta_T_load)/1000, 3) for m in m_load] # TODO: change
    load = [8.12, 8.07, 8.13, 8.57, 8.46, 8.51, 8.59, 8.55, 8.52, 7.4,
    6.69, 6.26, 5.87, 5.68, 5.52, 5.5, 5.92, 6.34, 6.49, 6.61, 6.74, 6.81, 6.94, 7.15]*20
    load = load[iter:iter+N] # because we are using fake data
    print(f"\nload = {load}")

    # Outside air tempecrature
    T_OA = [12]*N*int(1/delta_t_h) # TODO: get real forecasts!
    T_OA = [-12.52, -12.28, -12.55, -14.18, -13.76, -13.96, -14.26, -14.13,
    -13.99, -9.65, -6.86, -5.21, -3.69, -2.88, -2.36, -2.29, -3.91,
    -5.52, -6.13, -6.58, -7.09, -7.43, -7.99, -8.68]*20
    T_OA = T_OA[iter:iter+N] # because we are using fake data

    # Q_HP_max forecast from T_OA [kWh_th]
    Q_HP_max_list = [Q_HP_max(temp) for temp in T_OA]
    Q_HP_min_list = [8 for x in Q_HP_max_list]
    print(f"\nQ_HP_max = {Q_HP_max_list}")

    # 1/COP forecast from T_OA
    COP1_list = [COP1(temp) for temp in T_OA]
    print(f"\nCOP1_list = {COP1_list}")

    # ------------------------------------------
    # Get current state, estimate storage, set as initial
    # ------------------------------------------

    # Average temperature of tanks
    current_state = long_seq_pack['x_0']
    T_avg = sum(current_state)/16 - 273
    min_temp = 30
    current_storage = mass_of_water * 4187 * (T_avg - min_temp) * 2.77778e-7
    initial_storage = round(current_storage,1)
    print(f"\nCurrent storage = {initial_storage} kWh = {round(100*initial_storage/max_storage,1)} %")

    # ------------------------------------------
    # Solve closed loop with initial storage
    # ------------------------------------------
    
    # Get the solution from the optimization problem
    Q_opt, stor_opt, HP_on_off_opt, obj_opt = get_opti(N, c_el, load, max_storage, initial_storage, Q_HP_min_list, Q_HP_max_list, COP1_list)

    # Duplicate the last element of the hourly data for the plot
    c_el2 = c_el + [c_el[-1]]
    load2 = load + [load[-1]]
    Q_opt2 = [round(x,3) for x in Q_opt] + [Q_opt[-1]]
    Q_min2 = Q_HP_min_list + [Q_HP_min_list[-1]]
    Q_max2 = Q_HP_max_list + [Q_HP_max_list[-1]]

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
    
    HP_on_off_opt = [int(x) for x in HP_on_off_opt]
    print(HP_on_off_opt)
    return HP_on_off_opt

