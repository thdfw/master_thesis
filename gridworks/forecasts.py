import optimizer, forecasts
import csv
from datetime import datetime

'''
Input: index of desired start and end time steps
Output: list of forecasted electricty prices between start and end time steps
'''
# Get all electricity prices
def get_c_el(start, end, delta_t_h):

    # Electricity prices in cts/kWh, hourly prices for 24 hours
    c_el_all = [18.97, 18.92, 18.21, 16.58, 16.27, 15.49, 14.64, 18.93, 45.56, 26.42, 18.0, 17.17, 16.19, 30.74, 31.17, 16.18, 17.11, 20.24, 24.94, 24.69, 26.48, 30.15, 23.14, 24.11]
    
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
    return [20/1000/100]*15 + [20/1000/100]*30 + [20/1000/100]*15
    # return c_el_all[start:end]


'''
Input: index of desired start and end time steps
Output: list of forecasted mass flow rates going to the load between start and end time steps
'''
# Get all loads
def get_m_load(start, end, delta_t_h):

    # Loads in Wh (this is not the final data)
    Q_load_all = [310]*1000
    
    # Some constants
    cp = 4187
    Delta_T_load = 5/9*20
    
    # Corresponding mass flow rates in kg/s
    m_load_all = [Q_load/(delta_t_h*cp*Delta_T_load) for Q_load in Q_load_all]
    
    return m_load_all[start:end]


# ------------------------------------------------------
# Everything related to optimal sequence prediction
# ------------------------------------------------------

'''
Function to append the data to a CSV file
'''
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
    

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          60,
'time_step':        2,
}

# The four possible operating modes
operating_modes = [[0,0,0], [0,1,0], [1,0,1], [1,1,1]]

# The name of the CSV file for the results
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
csv_file_name = "results_" + formatted_datetime + ".csv"


'''
Input: current state and forecasts (through iter). A sequence and a horizon.
Output: cost of one step optimization over the given horizon.
'''
def one_iteration(x_0, iter, sequence, horizon):
    
    # Set the horizon
    pb_type['horizon'] = horizon
    
    # Get u* and x*
    u_opt, x_opt, obj_opt = optimizer.optimize_N_steps(x_0, 0, iter, pb_type, sequence, False)
    
    return round(obj_opt,3) #, x_opt, u_opt


'''
Input: current state and forecasts
Output: predicted optimal sequence of binary terms for the next N steps
'''
def get_optimal_sequence(x_0, iter):

    # ------------------------------------------------------
    # Initial state and forecasts
    # ------------------------------------------------------

    # Initial state of the buffer and storage tanks
    initial_state = x_0
    
    # Initialize
    min_cost = 1000
    optimals = []
    elec_prices = [round(100*1000*x,2) for x in forecasts.get_c_el(iter, iter+60, 2/60)]

    # Data going to the .csv file
    data = [{
        "T_B": [round(x,1) for x in initial_state[:4]],
        "T_S": [round(x,1) for x in initial_state[4:]],
        "iter": iter,
        "prices": [elec_prices[0], elec_prices[15], elec_prices[30], elec_prices[45]]
        }]
    
    print("\n#########################################")
    print(f"Buffer: {initial_state[:4]} \nStorage: {initial_state[4:]}")
    print(f"Electricity forecasts: {data[0]['prices']}")
    print("\nSearching for optimal sequence...")
    
    # ------------------------------------------------------
    # Find feasible combi1 over N=30min
    # ------------------------------------------------------
    for combi1 in operating_modes:
        
        sequence = {'combi1': combi1}
        cost = one_iteration(initial_state, iter, sequence, 15)
        print(f"\n******* combi1={combi1} *******")

        if cost == 1e5:
            print(f"combi1 = {combi1} is not feasible")
        
        else:
            print(f"combi1 = {combi1} has cost {cost} $. Testing for combi2:")
            
            # ------------------------------------------------------
            # Find feasible combi1, combi2 over N=1h
            # ------------------------------------------------------
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
                            for combi4 in operating_modes:
                            
                                sequence = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4}
                                cost = one_iteration(initial_state, iter, sequence, 60)
                                
                                if cost == 1e5:
                                    print(f"--- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} is not feasible.")
                                
                                else:
                                    print(f"--- combi1={combi1}, combi2={combi2}, combi3={combi3}, combi4={combi4} has cost {cost} $.")
                                    
                                    # ------------------------------------------------------
                                    # Compare to current minimum cost, update if better
                                    # ------------------------------------------------------
                                    
                                    if cost < min_cost:
                                        min_cost = cost
                                        optimals = {'combi1': combi1, 'combi2': combi2, 'combi3': combi3, 'combi4': combi4}
                                        
                                    if cost == 0.0:
                                        print(f"Minimum cost 0.0$ achieved for {optimals}")
                                        data[0]['sequence'] = [optimals['combi1'], optimals['combi2'], optimals['combi3'], optimals['combi4']]
                                        append_to_csv(csv_file_name, data)
                                        print("#########################################")
                                        return optimals

    # ------------------------------------------------------
    # Print and append the solution to CSV file
    # ------------------------------------------------------
    
    print(f"Minimum cost {round(min_cost,2)}$ achieved for {optimals}")
    data[0]['sequence'] = [optimals['combi1'], optimals['combi2'], optimals['combi3'], optimals['combi4']]
    append_to_csv(csv_file_name, data)
    print("#########################################")

    return optimals
