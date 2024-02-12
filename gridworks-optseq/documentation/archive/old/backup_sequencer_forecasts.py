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
