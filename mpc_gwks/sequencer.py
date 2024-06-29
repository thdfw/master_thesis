import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import casadi
import os
import datetime
import csv
import sys
import forecasts

PLOT = False
PRINT = False
BONMIN = True
delta_t_h = 4/60

# ------------------------------------------
# ------------------------------------------
# Gather parameters
# ------------------------------------------
# ------------------------------------------

# The maximum storage capacity (kWh)
mass_of_water = 450*4 # 450kg water per tank
max_temp, min_temp = 65, 38 #°C
max_storage = mass_of_water * 4187 * (max_temp - min_temp) # in Joules
max_storage = round(max_storage * 2.77778e-7,1) # in kWh

# The minimum storage capacity (kWh)
min_storage = 0
min_storage = mass_of_water * 4187 * (-1) # allow for 1°C below minimum temp
min_storage = round(min_storage * 2.77778e-7,1) # in kWh

if PRINT: print(f"Storage max: {max_storage}kWh, min: {min_storage}kWh")

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

def get_optimal_sequence(iter, previous_sequence, previous_attempt, results_file, attempt, current_state, pb_type):

    if attempt==1:
        # Print simulated date and time
        days = int(iter/24) + 1
        hours = iter%24
        print("\n-----------------------------------------------------")
        print(f"{hours}:00 - {hours+1}:00 (day {days})")
        print("-----------------------------------------------------")
        
    # ------------------------------------------
    # Get current state, estimate storage, set as initial
    # ------------------------------------------

    # Average temperature of tanks
    T_avg = sum(current_state)/16 - 273
    current_storage = mass_of_water * 4187 * (T_avg - min_temp) * 2.77778e-7
    initial_storage = round(current_storage,1)
    if attempt==1:
        print(f"\nCurrent storage level: {initial_storage} kWh ({round(100*initial_storage/max_storage,1)} %)")
    
    # If the current storage level is too high, turn off the HP during the first hour
    too_hot = True if current_storage > 45 else False
    
    # Horizon in hours
    N = int(pb_type['horizon'] * delta_t_h)
    
    # --------------------------------------------
    # If previous results were given (csv file)
    # --------------------------------------------
    
    if results_file != "":
    
        print(f"\n***** Reading sequence from provided csv file *****")
    
        # Read the csv as a pandas dataframe
        df = pd.read_csv(results_file)
        
        if iter < len(df):
    
            # Read the corresponding sequence in the file
            sequence_string = df['sequence'][iter]
            sequence_file_dict = {}
            for i in range(1,N+1):
                combi = sequence_string[2+(i-1)*11:9+(i-1)*11].split(",")
                sequence_file_dict[f'combi{i}'] = [int(combi[0]), int(combi[1]), int(combi[2])]
            
            return sequence_file_dict
            
    print(f"\n***** Attempt {attempt} of finding the optimal sequence *****") if attempt>1 else print("")
    
    # ------------------------------------------
    # Get current forecasts
    # ------------------------------------------
    
    # Price
    c_el = [round(x*1000*100,2) for x in forecasts.get_c_el(iter, iter+N, 1)]
    if PRINT: print(f"\nc_el = {c_el}")

    # Load
    cp, Delta_T_load = 4187,  5/9*20
    m_load = forecasts.get_m_load(iter, iter+N, 1)
    load = [round((m*cp*Delta_T_load)/1000, 3) for m in m_load] # TODO: change
    if PRINT: print(f"\nload = {load}")

    # Outside air tempecrature
    T_OA = [12]*N # TODO: get real forecasts!

    # Q_HP_max forecast from T_OA [kWh_th]
    Q_HP_max_list = [Q_HP_max(temp) for temp in T_OA]
    Q_HP_min_list = [8 for x in Q_HP_max_list]
    if PRINT: print(f"\nQ_HP_max = {Q_HP_max_list}")

    # 1/COP forecast from T_OA
    COP1_list = [COP1(temp) for temp in T_OA]
    if PRINT: print(f"\nCOP1_list = {COP1_list}")

    # ------------------------------------------
    # Solve closed loop with initial storage
    # ------------------------------------------
    
    # Get the solution from the optimization problem
    Q_opt, stor_opt, HP_on_off_opt, obj_opt = get_opti(N, c_el, load, max_storage, initial_storage, Q_HP_min_list, Q_HP_max_list, COP1_list, too_hot)

    # Duplicate the last element of the hourly data for the plot
    c_el2 = c_el + [c_el[-1]]
    load2 = load + [load[-1]]
    Q_opt2 = [round(x,3) for x in Q_opt] + [Q_opt[-1]]
    Q_min2 = Q_HP_min_list + [Q_HP_min_list[-1]]
    Q_max2 = Q_HP_max_list + [Q_HP_max_list[-1]]

    # Plot
    if PLOT:
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
    # Find operating hours
    # ------------------------------------------
    
    # From optimization problem
    HP_on_off_opt = [int(x) for x in HP_on_off_opt]
    backup = HP_on_off_opt
    solver_name = "bonmin" if BONMIN else "gurobi"
    
    if attempt == 1:
        print(f"On/Off sequence from MILP ({solver_name}):\n{HP_on_off_opt}")
    
    # Solve the optimization problem with an increased load
    if attempt > 1:
        
        # Increase the load by the amount it has been increased in the latest attempt
        attempt = 0
        while [int(x) for x in HP_on_off_opt] != previous_attempt:
            attempt += 1
            load_increased = [round((1+(attempt-1)*0.01)*x,5) for x in load]
            Q_opt, stor_opt, HP_on_off_opt, obj_opt = get_opti(N, c_el, load_increased, max_storage, initial_storage, Q_HP_min_list, Q_HP_max_list, COP1_list, too_hot)
            
        if PRINT: print(f"Got back to previous try, which was increasing load by {(attempt-1)*1}%")
        
        if PRINT: print(f"\nBackup:\n{backup}")
        if PRINT: print(f"\nPrevious attempt:\n{previous_attempt}")
        if PRINT: print(f"\nCurrent:\n{[int(x) for x in HP_on_off_opt]}")

        # Increase the load as long as the operating hours are the same
        while [int(x) for x in HP_on_off_opt] == backup or [int(x) for x in HP_on_off_opt]==previous_attempt:
    
            # Increase the load 1% at a time until the sequence changes from previous attempt
            load_increased = [round((1+(attempt-1)*0.01)*x,5) for x in load]

            # Get the recommendation for the increased load
            Q_opt, stor_opt, HP_on_off_opt, obj_opt = get_opti(N, c_el, load_increased, max_storage, initial_storage, Q_HP_min_list, Q_HP_max_list, COP1_list, too_hot)
            
            # Next iteration if no operating hour change
            attempt += 1
        
        HP_on_off_opt = [int(x) for x in HP_on_off_opt]
        print(f"On/Off after increasing load by {(attempt-2)*1}%:\n{HP_on_off_opt}")
        
    # ------------------------------------------
    # Convert to combi and return sequence
    # ------------------------------------------

    print("")
    sequence_combi = {}
    for i in range(N):
        sequence_combi[f'combi{i+1}'] = [1,1,1] if HP_on_off_opt[i]==1 else [0,0,0]
    
    return sequence_combi, HP_on_off_opt

# ------------------------------------------
# ------------------------------------------
# MINLP optimization problem
# ------------------------------------------
# ------------------------------------------

def get_opti(N, c_el, load, max_storage, storage_initial, Q_HP_min_list, Q_HP_max_list, COP1_list, too_hot):

    # Initialize
    opti = casadi.Opti() if BONMIN else casadi.Opti('conic')

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
    if BONMIN:
        opti.solver('bonmin', {'discrete': discrete_var, 'bonmin.tol': 1e-4, 'bonmin.print_level': 0, 'print_time': 0})
    else:
        opti.solver('gurobi', {'discrete':discrete_var, 'gurobi.OutputFlag':0})

    # -----------------------------
    # Constraints
    # -----------------------------

    # Initial storage level
    opti.subject_to(storage[0] == storage_initial)

    # Constraints at every time step
    for t in range(N+1):

        # Bounds on storage (allow for negative storage in first hour, means the water is below 311K)
        if t>0: opti.subject_to(storage[t] >= min_storage)
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
            
    # First hour
    if too_hot:
        print("The heat pump must be turned off in the next hour, since the tanks are too hot to further charge.")
        opti.subject_to(delta_HP[0] == 0)

    # -----------------------------
    # Objective
    # -----------------------------

    obj = sum(Q_HP_onoff[t]*c_el[t]*COP1_list[t] for t in range(N))
    opti.minimize(obj)

    # -----------------------------
    # Solve and get optimal values
    # -----------------------------

    sys.stdout = open(os.devnull, 'w')
    sol = opti.solve()
    sys.stdout = sys.__stdout__
    
    Q_opt = sol.value(Q_HP_onoff)
    stor_opt = sol.value(storage)
    HP_on_off_opt = sol.value(delta_HP)
    obj_opt = round(sol.value(obj)/100,2)

    return Q_opt, stor_opt, HP_on_off_opt, obj_opt



# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Save result in a CSV file
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# The name of the CSV file for the results
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
csv_file_name = os.path.join("data", "simulations", "recent", "results_" + formatted_datetime + ".csv")

def append_to_csv(x_0, iter, sequence, pb_type):

    N = int(pb_type['horizon'] * delta_t_h)

    csv_data = [{
        "T_B": [round(x,1) for x in x_0[:4]],
        "T_S": [round(x,1) for x in x_0[4:]],
        "iter": iter,
        "prices": [round(x*1000*100,2) for x in forecasts.get_c_el(iter, iter+N, 1)],
        "loads": forecasts.get_m_load(iter, iter+N, 1),
        "sequence": [sequence[f'combi{i}'] for i in range(1,N+1)]
    }]
    
    with open(csv_file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["T_B", "T_S", "prices", "loads", "iter", "sequence"])
        
        # If file is empty, write headers
        if file.tell() == 0:
            writer.writeheader()
        
        # Append data to CSV
        for row in csv_data:
            writer.writerow(row)
            
    print("Data was appended to", csv_file_name)