import numpy as np
import csv
from datetime import datetime
import optimizer, plot, functions

'''
Input: index of desired start and end time steps
Output: list of forecasted electricty prices between start and end time steps
'''
# Get all electricity prices
def get_c_el(start, end, delta_t_h):

    # Electricity prices in cts/kWh, hourly prices for 24 hours
    #c_el_all = [18.97, 18.92, 18.21, 16.58, 16.27, 15.49, 14.64, 18.93, 45.56, 26.42, 18.0, 17.17, 16.19, 30.74, 31.17, 16.18, 17.11, 20.24, 24.94, 24.69, 26.48, 30.15, 23.14, 24.11]
    c_el_all = [14.64, 18.93, 45.56, 26.42, 18.0, 17.17, 16.19, 30.74, 31.17, 16.18, 17.11, 20.24, 24.94, 24.69, 26.48, 30.15, 23.14, 24.11, 18.97, 18.92, 18.21, 16.58, 16.27, 15.49]
    c_el_all = [6.36, 6.34, 6.34, 6.37, 6.41, 6.46, 6.95, 41.51, 41.16, 41.07, 41.06, 41.08, 7.16, 7.18, 7.18, 7.16, 41.2, 41.64, 41.43, 41.51, 6.84, 6.65, 6.46, 6.4] # cluster 4

    # The number of time steps that make up one hour
    time_steps = int(1/delta_t_h)
    if int(1/delta_t_h) != 1/delta_t_h: raise ValueError("The chosen time step does not add up to an hour.")
    
    # Extend to match time step (1 hour is 1/delta_t_h time steps)
    c_el_all = [item for item in c_el_all for _ in range(time_steps)]
        
    # Convert to $/Wh
    c_el_all = [x/100/1000 for x in c_el_all]
    
    # Duplicate days
    c_el_all = c_el_all*30
    
    #return [18.93/1000/100]*15 + [45.56/1000/100]*30 + [26.42/1000/100]*15
    return c_el_all[start:end]


'''
Input: index of desired start and end time steps
Output: list of forecasted mass flow rates going to the load between start and end time steps
'''
# Get all loads
def get_m_load(start, end, delta_t_h):

    # Hourly average heating power [kW] -> [W]
    Q_load_all = [5.91, 5.77, 5.67, 5.77, 5.71, 6.06, 6.34, 6.34, 6.01, 5.77, 5.05, 5.05, 4.91, 4.91, 4.91, 4.91, 5.05, 5.1, 4.91, 4.91, 4.91, 4.91, 4.98, 4.91]
    Q_load_all = [item*1000 for item in Q_load_all]
    
    # Corresponding mass flow rates in kg/s
    cp, Delta_T_load = 4187,  5/9*20
    m_load_all = [round(Q_load/(cp*Delta_T_load), 3) for Q_load in Q_load_all]
    
    # Extend to match time step (1 hour is 1/delta_t_h time steps)
    m_load_all = [item for item in m_load_all for _ in range(int(1/delta_t_h))]
    
    # intermediate cluster
    # m_load_all = [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.1, 0.1, 0.08, 0.08, 0.08, 0.08, 0.08, 0.07, 0.07, 0.07, 0.07, 0.07, 0.09, 0.09, 0.1, 0.1, 0.11, 0.11]
    
    # Duplicate days
    m_load_all = m_load_all*30
    
    return m_load_all[start] if end-start==1 else m_load_all[start:end]
    

'''
Input: index of desired start and end time steps
Output: list of forecasted outside air temperatures
'''
# Get all outside temperatures
def get_T_OA(start, end, delta_t_h):
    
    # Outside air temperature in K
    T_OA_all = [273+12]*1000

    # Get 1/COP from the T_OA with linear regression
    B0_C, B1_C = 2.695868, -0.008533
    COP1_all = [round(B0_C + B1_C*T_OA_all[i],4) for i in range(len(T_OA_all))]

    # Get Q_HP_max from the T_OA with linear regression
    B0_Q, B1_Q = -68851.589, 313.3151
    Q_HP_max_all = [round(B0_Q + B1_Q*T_OA_all[i],2) if T_OA_all[i]<(273-7) else 14000 for i in range(len(T_OA_all))]
    
    return COP1_all[start:end], Q_HP_max_all[start:end]


# ------------------------------------------------------
# Everything related to optimal sequence prediction
# ------------------------------------------------------

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          120,
'time_step':        4,
}

# The four possible operating modes
operating_modes = [[0,0,0], [1,1,1], [0,1,0], [1,0,1]]

# The name of the CSV file for the results
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
csv_file_name = "results_" + formatted_datetime + ".csv"

# ------------------------------------------------------
# Append data to CSV file
# ------------------------------------------------------

def append_to_csv(file_name, data):
        
    with open(file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["T_B", "T_S", "prices", "iter", "sequence"])
        
        # If file is empty, write headers
        if file.tell() == 0:
            writer.writeheader()
        
        # Append data to CSV
        for row in data:
            writer.writerow(row)
            
    print("Data was appended to", file_name)
    

# ------------------------------------------------------
# One iteration of the optimization algorithm
# ------------------------------------------------------
'''
Input: current state and forecasts (through iter). A sequence and a horizon.
Output: cost of one step optimization over the given horizon.
'''
def one_iteration(x_0, iter, sequence, horizon, x_opt_prev, u_opt_prev):

    # Warm start the solver with the previous MPC solution

    if horizon < 105:
        until = -(105-horizon)
        initial_x = [[float(x) for x in x_opt_prev[k,-106:until]] for k in range(16)]
        initial_u = [[float(u) for u in u_opt_prev[k,-105:until]] for k in range(6)]
        
    if horizon == 105:
        initial_x = [[float(x) for x in x_opt_prev[k,-106:]] for k in range(16)]
        initial_u = [[float(u) for u in u_opt_prev[k,-105:]] for k in range(6)]
    
    if horizon == 120:
        initial_x = [[float(x) for x in x_opt_prev[k,-106:]] for k in range(16)]
        initial_u = [[float(u) for u in u_opt_prev[k,-105:]] for k in range(6)]
        initial_x = np.array([initial_x_i+[0]*15 for initial_x_i in initial_x])
        initial_u = np.array([initial_u_i+[0]*15 for initial_u_i in initial_u])

    # Set the warm start
    warm_start = {'initial_x': np.array(initial_x), 'initial_u': np.array(initial_u)}
        
    # Set the horizon
    pb_type['horizon'] = horizon

    # Get u* and x*
    u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, 0, iter, pb_type, sequence, warm_start, False)
        
    return obj_opt, x_opt, u_opt, error


# ------------------------------------------------------
# Get the optimal sequence for the next N steps
# ------------------------------------------------------
'''
Input: current state and forecasts
Output: optimal sequence of binary terms for the next N steps
'''
def get_optimal_sequence(x_0, iter, x_opt_prev, u_opt_prev):

    # ------------------------------------------------------
    # Initial state and forecasts
    # ------------------------------------------------------

    # Initial state of the buffer and storage tanks
    initial_state = x_0
    
    # Initialize
    delta_t_h = 4/60
    min_cost = 1e6
    optimals = []
    elec_prices = [round(100*1000*x,2) for x in get_c_el(iter, iter+120, delta_t_h)]
    elec_prices = [elec_prices[i*15] for i in range(8)]
    price_treshold = 20
    COP1, Q_HP_max = get_T_OA(iter, iter+120, delta_t_h)
    COP1_avg = [sum(COP1[15*i:15*(i+1)])/15 for i in range(8)]

    # Data going to the .csv file
    data = [{
        "T_B": [round(x,1) for x in initial_state[:4]],
        "T_S": [round(x,1) for x in initial_state[4:]],
        "iter": iter,
        "prices": elec_prices
        }]
    
    print("\n#########################################")
    print(f"Buffer: {initial_state[:4]} \nStorage: {initial_state[4:]}")
    print(f"Electricity forecasts: {data[0]['prices']}")
    print("\nSearching for optimal sequence...")
    
    # ------------------------------------------------------
    # Find feasible combi1 over N=1h
    # ------------------------------------------------------
    for combi1 in operating_modes:
    
        if (elec_prices[0]>=price_treshold) and (combi1[2] == 1): continue
        if (elec_prices[0]<price_treshold) and (combi1[2] == 0): continue

        print(f"\n******* combi1={combi1} *******")

        # If the HP will be on, and at the minimum power, and the price is higher than the current minimum, skip
        if (combi1[2] == 1) and (elec_prices[0]/1000/100 * delta_t_h * 8000 * 15 * COP1_avg[0] > min_cost):
            print(f"combi1 = {combi1} will be more expensive than current minimum")
            continue
            
        sequence = {'combi1': combi1}
        cost1, x_opt, u_opt, error = one_iteration(initial_state, iter, sequence, 15, x_opt_prev, u_opt_prev)

        if cost1 == 1e5:
            print(f"combi1 = {combi1} could not be solved: {error}")
        
        else:
            if cost1 > min_cost:
                print(f"combi1 = {combi1} is feasible but more expensive than current minimum")
                continue
            else:
                print(f"combi1 = {combi1} is feasible. Testing for combi2:")

            # ------------------------------------------------------
            # Find feasible combi1, combi2 over N=2h
            # ------------------------------------------------------
            for combi2 in operating_modes:
            
                if (elec_prices[1]>=price_treshold) and (combi2[2] == 1): continue
                if (elec_prices[1]<price_treshold) and (combi2[2] == 0): continue
            
                # If the HP will be on, and at the minimum power, and the price is higher than the current minimum, skip
                if (combi2[2] == 1) and (cost1 + (elec_prices[1]/1000/100 * delta_t_h * 8000 * 15 * COP1_avg[1]) > min_cost):
                    print(f"- combi1={combi1}, combi2={combi2} will be more expensive than current minimum")
                    continue
            
                sequence = {'combi1': combi1, 'combi2': combi2}
                cost2, x_opt, u_opt, error = one_iteration(initial_state, iter, sequence, 30, x_opt_prev, u_opt_prev)
                
                if cost2 == 1e5:
                    print(f"- combi1={combi1}, combi2={combi2} could not be solved: {error}")
                
                else:
                    if cost2 > min_cost:
                        print(f"- combi1={combi1}, combi2={combi2} is feasible but more expensive than current minimum")
                        continue
                    else:
                        print(f"- combi1={combi1}, combi2={combi2} is feasible. Testing for combi3:")

                    # ------------------------------------------------------
                    # Find feasible combi1, combi2, combi3 over N=3h
                    # ------------------------------------------------------
                    for combi3 in operating_modes:
                    
                        if (elec_prices[2]>=price_treshold) and (combi3[2] == 1): continue
                        if (elec_prices[2]<price_treshold) and (combi3[2] == 0): continue
                    
                        # If the HP will be on, and at the minimum power, and the price is higher than the current minimum, skip
                        if (combi3[2] == 1) and (cost2 + (elec_prices[2]/1000/100 * delta_t_h * 8000 * 15 * COP1_avg[2]) > min_cost):
                            print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3} will be more expensive than current minimum")
                            continue
                    
                        sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3}
                        cost3, x_opt, u_opt, error = one_iteration(initial_state, iter, sequence, 45, x_opt_prev, u_opt_prev)
                        
                        if cost3 == 1e5:
                            print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3} could not be solved: {error}")
                        
                        else:
                            if cost3 > min_cost:
                                print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3} is feasible but more expensive than current minimum")
                                continue
                            else:
                                print(f"-- combi1={combi1}, combi2={combi2}, combi3={combi3} is feasible. Testing for combi4:")

                            # ------------------------------------------------------
                            # Find feasible combi1, combi2, combi3, combi4 over N=4h
                            # ------------------------------------------------------
                            for combi4 in operating_modes:
                            
                                if (elec_prices[3]>=price_treshold) and (combi4[2] == 1): continue
                                if (elec_prices[3]<price_treshold) and (combi4[2] == 0): continue
                            
                                # If the HP will be on, and at the minimum power, and the price is higher than the current minimum, skip
                                if (combi4[2] == 1) and (cost3 + (elec_prices[3]/1000/100 * delta_t_h * 8000 * 15 * COP1_avg[3]) > min_cost):
                                    print(f"--- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} will be more expensive than current minimum")
                                    continue
                            
                                sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4}
                                cost4, x_opt, u_opt, error = one_iteration(initial_state, iter, sequence, 60, x_opt_prev, u_opt_prev)
                                
                                if cost4 == 1e5:
                                    print(f"--- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} could not be solved: {error}")
                                
                                else:
                                    print(f"--- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} is feasible. Testing for combi5:")
                                    
                                    # ------------------------------------------------------
                                    # Find feasible combi1, ..., combi5 over N=5h
                                    # ------------------------------------------------------
                                    for combi5 in operating_modes:
                                    
                                        if (elec_prices[4]>=price_treshold) and (combi5[2] == 1): continue
                                        if (elec_prices[4]<price_treshold) and (combi5[2] == 0): continue
                                    
                                        # If the HP will be on, and at the minimum power, and the price is higher than the current minimum, skip
                                        if (combi5[2] == 1) and (cost4 + (elec_prices[4]/1000/100 * delta_t_h * 8000 * 15 * COP1_avg[4]) > min_cost):
                                            print(f"---- combi1={combi1}, ..., combi5={combi5} will be more expensive than current minimum")
                                            continue
                                    
                                        sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4, 'combi5': combi5}
                                        cost5, x_opt, u_opt, error = one_iteration(initial_state, iter, sequence, 75, x_opt_prev, u_opt_prev)
                                        
                                        if cost5 == 1e5:
                                            print(f"---- combi1={combi1}, ..., combi5={combi5} could not be solved: {error}")
                                        
                                        else:
                                            print(f"---- combi1={combi1}, ..., combi5={combi5} is feasible. Testing for combi6:")
                                            
                                            # ------------------------------------------------------
                                            # Find feasible combi1, ..., combi6 over N=6h
                                            # ------------------------------------------------------
                                            for combi6 in operating_modes:
                                            
                                                if (elec_prices[5]>=price_treshold) and (combi6[2] == 1): continue
                                                if (elec_prices[5]<price_treshold) and (combi6[2] == 0): continue
                                            
                                                # If the HP will be on, and at the minimum power, and the price is higher than the current minimum, skip
                                                if (combi6[2] == 1) and (cost5 + (elec_prices[5]/1000/100 * delta_t_h * 8000 * 15 * COP1_avg[5]) > min_cost):
                                                    print(f"----- combi1={combi1}, ..., combi6={combi6} will be more expensive than current minimum")
                                                    continue
                                            
                                                sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4, 'combi5': combi5, 'combi6': combi6}
                                                cost6, x_opt, u_opt, error = one_iteration(initial_state, iter, sequence, 90, x_opt_prev, u_opt_prev)
                                                
                                                if cost6 == 1e5:
                                                    print(f"----- combi1={combi1}, ..., combi6={combi6} could not be solved: {error}")
                                                
                                                else:
                                                    print(f"----- combi1={combi1}, ..., combi6={combi6} is feasible. Testing for combi7:")
                                                    
                                                    # ------------------------------------------------------
                                                    # Find feasible combi1, ..., combi7 over N=7h
                                                    # ------------------------------------------------------
                                                    for combi7 in operating_modes:
                                                    
                                                        if (elec_prices[6]>=price_treshold) and (combi7[2] == 1): continue
                                                        if (elec_prices[6]<price_treshold) and (combi7[2] == 0): continue
                                                    
                                                        # If the HP will be on, and at the minimum power, and the price is higher than the current minimum, skip
                                                        if (combi7[2] == 1) and (cost6 + (elec_prices[6]/1000/100 * delta_t_h * 8000 * 15 * COP1_avg[6]) > min_cost):
                                                            print(f"------ combi1={combi1}, ..., combi7={combi7} will be more expensive than current minimum")
                                                            continue
                                                    
                                                        sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4, 'combi5': combi5, 'combi6': combi6, 'combi7': combi7}
                                                        cost7, x_opt, u_opt, error = one_iteration(initial_state, iter, sequence, 105, x_opt_prev, u_opt_prev)
                                                        
                                                        if cost7 == 1e5:
                                                            print(f"------ combi1={combi1}, ..., combi7={combi7} could not be solved: {error}")
                                                        
                                                        else:
                                                            print(f"------ combi1={combi1}, ..., combi7={combi7} is feasible. Testing for combi8:")
                                                            
                                                            # ------------------------------------------------------
                                                            # Find feasible combi1, ..., combi8 over N=8h
                                                            # ------------------------------------------------------
                                                            for combi8 in operating_modes:
                                                            
                                                                if (elec_prices[7]>=price_treshold) and (combi8[2] == 1): continue
                                                                if (elec_prices[7]<price_treshold) and (combi8[2] == 0): continue
                                                            
                                                                # If the HP will be on, and at the minimum power, and the price is higher than the current minimum, skip
                                                                if (combi8[2] == 1) and (cost7 + (elec_prices[7]/1000/100 * delta_t_h * 8000 * 15 * COP1_avg[7]) > min_cost):
                                                                    print(f"----- combi1={combi1}, ..., combi8={combi8} will be more expensive than current minimum")
                                                                    continue
                                                            
                                                                sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4, 'combi5': combi5, 'combi6': combi6, 'combi7': combi7, 'combi8': combi8}
                                                                cost8, x_opt, u_opt, error = one_iteration(initial_state, iter, sequence, 120, x_opt_prev, u_opt_prev)
                                                                
                                                                if cost8 == 1e5:
                                                                    print(f"------- combi1={combi1}, ..., combi8={combi8} could not be solved: {error}")
                                                                
                                                                else:
                                                                    print(f"------- combi1={combi1}, ..., combi8={combi8} has cost {cost8}")

                                                                # ------------------------------------------------------
                                                                # Compare to current minimum cost, update if better
                                                                # ------------------------------------------------------
                                                                
                                                                if cost8 < min_cost and cost8 != 1e5:
                                                                    min_cost = cost8
                                                                    optimals = sequence

                                                                    # ------------------------------------------------------
                                                                    # Print and append the solution to CSV file
                                                                    # ------------------------------------------------------
                                                                    
                                                                    print(f"Minimum cost {round(min_cost,2)}$ achieved for {optimals}")
                                                                    data[0]['sequence'] = [optimals[f'combi{i}'] for i in range(1,9)]
                                                                    append_to_csv(csv_file_name, data)
                                                                    print("#########################################")
                                                                    
                                                                    return optimals
