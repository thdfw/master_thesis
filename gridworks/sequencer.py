import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import optimizer

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Main get sequence function
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------

def get_sequence(c_el, m_load, iter, previous_sequence, results_file, attempt, long_seq_pack):
    
    PLOT, PRINT = False, False

    # --------------------------------------------
    # If a previous results (csv file) were given
    # --------------------------------------------
    
    if results_file != "" and iter < len(df):
    
        # Read the csv as a pandas dataframe
        df = pd.read_csv(results_file)
    
        # Read the corresponding sequence in the file
        sequence_string = df['sequence'][iter]
        sequence_file_dict = {}
        for i in range(1,9):
            combi = sequence_string[2+(i-1)*11:9+(i-1)*11].split(",")
            sequence_file_dict[f'combi{i}'] = [int(combi[0]), int(combi[1]), int(combi[2])]
        
        return sequence_file_dict
    
    # --------------------------------------------
    # For all attempts: get pre-maid sequence
    # --------------------------------------------
    
    # Get the hour of the day
    hour = iter%24
    
    # Initialize the sequence with all '2' (0=off, 1=on, 2=undetermined)
    sequence = 2*np.ones(len(c_el))

    # Depending on the type of load, the sequence will not be the same
    if round(np.mean(m_load),2) >= 0.10: load_type = "High load"
    elif round(np.mean(m_load),2) >= 0.05: load_type = "Medium load"
    else: load_type = "Low load"
    if PRINT: print(load_type)
        
    # For every hour in the next 24 hours
    for i in range(len(c_el)):

        # Always turn off the heat pump in high price periods
        if c_el[i] > 20: sequence[i] = 0

        # Always turn on the heat pump in negative price periods
        if c_el[i] < 0: sequence[i] = 1

        # Detect peaks, and their length
        if i<(len(c_el)-1) and abs(c_el[i+1] - c_el[i]) >= 15:
            if c_el[i+1] - c_el[i] > 0 and c_el[i+1]>20:
                length = i
                if PRINT: print(f"Price peak starting at {i+1}h")
            if c_el[i+1] - c_el[i] < 0  and c_el[i]>20:
                length = i - length
                if PRINT: print(f"Price peak finishing at {i+1}h, after {length} hours\n")

                # Depending on the load type, the minimum number of hours to charge before an x hour peak is not the same
                if load_type == "High load":
                    hours_charge = length
                elif load_type == "Medium load":
                    hours_charge = int(round(length/2 + 0.001)) if length>=2 else 1
                elif load_type == "Low load":
                    # hours_charge = int(round(length/3 + 0.001)) if length>=3 else 1
                    # With low loads it might not be necessary to charge, leave undecided
                    hours_charge = 0

                # Charge the tanks for as long as necessary before the peak
                for j in range(hours_charge):
                    # Hours that are still undefined are turned on
                    if sequence[i-length-j] == 2:
                        sequence[i-length-j] = 1
                    # Hours that were supposed to be turned off are turned on (this setting can change)
                    if sequence[i-length-j] == 0:
                        sequence[i-length-j] = 1
                        if hour < i-length+3-hours_charge:
                            print(f"\nNeed to charge more before peak {i+1-length}h-{i+1}h.")
                            print("Current setting is to use normally off periods to charge.")

    # Save the suggested sequence with 0=off, 1=on, 2=undetermined
    sequence012 = [int(x) for x in sequence[hour:hour+8]]
    
    # Get the indices of the hours with remaining undertermined state
    two_option_indices = [1 if x==2 else np.nan for x in sequence]

    # If the current hour is in an undetermined state, try running it with the HP off
    if sequence[hour] == 2: sequence[hour] = 0
        
    # All other undetermined hours are kept as on for now (as long as it is not their turn)
    sequence = [1 if x==2 else int(x) for x in sequence]

    if PLOT:
        
        # Split electricity price in past and future hours
        c_el_future = [np.nan]*(hour-1) + c_el[hour-1:] if hour>0 else [np.nan]*(hour) + c_el[hour:]
        c_el_past = c_el[:hour] + [np.nan]*(len(c_el)-hour)

        # Split sequence in past and future hours
        sequence_future = [np.nan]*(hour-1) + sequence[hour-1:] if hour>0 else [np.nan]*hour + sequence[hour:]
        sequence_past = sequence[:hour] + [np.nan]*(len(c_el)-hour)

        # Highlight hours with undetermined mode
        two_option_indices_plot = [np.nan]*hour + two_option_indices[hour:]

        # Duplicate the final element of each plotted list to extend it midnight
        c_el_future = c_el_future + [c_el_future[-1]]
        c_el_past = c_el_past + [c_el_past[-1]]
        sequence_future = sequence_future + [sequence_future[-1]]
        sequence_past = sequence_past + [sequence_past[-1]]
        two_option_indices_plot = two_option_indices_plot + [two_option_indices_plot[-1]]
        
        # Plot the past and future electricity prices and load
        fig, ax = plt.subplots(1,1, figsize=(12,4), sharex=True)
        ax.step(range(len(c_el)+1), c_el_future, where='post', alpha=0.4, color='black', linestyle='dashed')
        ax.step(range(len(c_el)+1), c_el_past, where='post', alpha=0.6, color='black')
        ax.set_xticks(range(len(c_el)+1))
        ax.set_xlim([-1,len(c_el)+1])
        ax.set_ylim([-10,45])
        ax2 = ax.twinx()
        ax2.step(range(len(c_el)+1), sequence_future, where='post', color='blue', alpha=0.6, linestyle='dashed')
        ax2.step(range(len(c_el)+1), sequence_past, where='post', color='blue', alpha=0.6)
        ax2.step(range(len(c_el)+1), two_option_indices_plot, where='post', color='red', alpha=0.9)
        ax2.set_yticks([0,1])
        ax2.set_ylim([-0.7,1.7])
        
        # Highlight the area corresponding to the horizon
        plt.axvline(x=hour, color='green', linestyle='dotted',alpha=0.2)
        plt.axvline(x=hour+8, color='green', linestyle='dotted',alpha=0.2)
        plt.axvspan(hour, hour+8, facecolor='green', alpha=0.05, label='Highlight')
        
        # Plot title
        plt.title(f"{load_type}") if two_option_indices[hour]!=1 else plt.title(f"{load_type} - two options")
        plt.show()

    # Trim the sequence to fit the 8-hour horizon
    sequence_trimmed = sequence[hour:hour+8]
    
    # Convert to combination format
    sequence_trimmed = [[1,1,1] if x==1 else [0,0,0] for x in sequence_trimmed]
    sequence_dict = {}
    for i in range(len(sequence_trimmed)):
        sequence_dict[f'combi{i+1}'] = sequence_trimmed[i]

    # Report if there are two options (current mode is undetermined)
    undertermined_now = two_option_indices[hour] == 1
    
    # Update the sequence with previous results
    #print("Previous sequence:\n", previous_sequence)
    #print("Current sequence before comparison:\n", sequence_dict)
    for i in range(1,9):
        # If there is a [0,0,0] -> [0,1,0] change in previous sequence
        if i<8 and sequence_dict[f'combi{i}'] == [0,0,0] and previous_sequence[f'combi{i+1}'] == [0,1,0]:
            sequence_dict[f'combi{i}'] = [0,1,0]
            print(f"Replaced [0,0,0] with [0,1,0] in combi{i}")
        # If there is a [1,1,1] -> [1,0,1] change in previous sequence
        if i<8 and sequence_dict[f'combi{i}'] == [1,1,1] and previous_sequence[f'combi{i+1}'] == [1,0,1]:
            sequence_dict[f'combi{i}'] = [1,0,1]
            print(f"Replaced [1,1,1] with [1,0,1] in combi{i}")
        if i<8 and sequence_dict[f'combi{i}'] == [1,1,1] and previous_sequence[f'combi{i+1}'] == [0,0,0]:
            sequence_dict[f'combi{i}'] = [0,0,0]
            print(f"Replaced [1,1,1] with [0,0,0] in combi{i}")

    # --------------------------------------------
    # Attempt 1: use pre-maid sequence
    # Next attempts: adjust pre-maid sequence
    # Final attempts: run through all sequences
    # --------------------------------------------

    if PRINT: print("There are two options") if undertermined_now==True else print("Only one option")
    
    if attempt == 1:
        if load_type == "Low load": sequence_dict = long_sequence_check(iter, sequence012, long_seq_pack, c_el[hour:hour+8])
        return sequence_dict
    
    if undertermined_now == True:
        if attempt == 2:
            sequence_dict['combi1'] = [0,1,0]
        if attempt == 3:
            sequence_dict['combi1'] = [1,1,1]
        if attempt == 4:
            sequence_dict = long_sequence_check(iter, sequence012, long_seq_pack, c_el[hour:hour+8])
        if attempt > 4:
            raise ValueError("No feasible sequence was found!")
        return sequence_dict

    else:
        if attempt == 2:
            if sequence_dict['combi8'] != [0,0,0]: sequence_dict['combi8'] = [0,0,0]
            else: attempt += 1
        if attempt == 3:
            sequence_dict = long_sequence_check(iter, sequence012, long_seq_pack, c_el[hour:hour+8])
        if attempt > 3:
            raise ValueError("No feasible sequence was found!")
        return sequence_dict


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# If nothing works, go through long check
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          120,
'time_step':        4,
}

# The four possible operating modes, in the order to be checked
operating_modes = [[0,0,0], [1,1,1], [0,1,0], [1,0,1]]

# ------------------------------------------------------
# One iteration of the optimization problem
# ------------------------------------------------------

def one_iteration(x_0, iter, sequence, horizon, x_opt_prev, u_opt_prev):

    # For anything below an 8-hour horizon, warm start with the previous solution
    if horizon < 105:
        initial_x = [[float(x) for x in x_opt_prev[k,-106:-(105-horizon)]] for k in range(16)]
        initial_u = [[float(u) for u in u_opt_prev[k,-105:-(105-horizon)]] for k in range(6)]
    else:
        initial_x = [[float(x) for x in x_opt_prev[k,-106:]] for k in range(16)]
        initial_u = [[float(u) for u in u_opt_prev[k,-105:]] for k in range(6)]
    
    # For a full 8 hour horizon, warm start with previous solution and add zeros for the final hour
    if horizon == 120:
        initial_x = np.array([initial_x_i+[0]*15 for initial_x_i in initial_x])
        initial_u = np.array([initial_u_i+[0]*15 for initial_u_i in initial_u])

    # Put the warm start in the required format
    warm_start = {'initial_x': np.array(initial_x), 'initial_u': np.array(initial_u)}
        
    # Set the horizon
    pb_type['horizon'] = horizon

    # Get u* and x*
    u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, 0, iter, pb_type, sequence, warm_start, False)
        
    return obj_opt, x_opt, u_opt, error

# ------------------------------------------------------
# The long check
# ------------------------------------------------------

def long_sequence_check(iter, sequence012, long_seq_pack, elec_prices):
    
    # Unpack values for long sequence check
    x_0 = long_seq_pack['x_0']
    x_opt_prev = long_seq_pack['x_opt_prev']
    u_opt_prev = long_seq_pack['u_opt_prev']
    
    print("\n#########################################")
    print(f"Buffer: {x_0[:4]} \nStorage: {x_0[4:]}")
    print(f"Electricity forecasts: {elec_prices}")
    print(f"Sequence suggestion: {sequence012}")
    print("\nSearching for feasible sequence...")

    # Initialize
    sequence = {}
    
    for step in range(1,9):
    
        solved = False
        
        for combi in operating_modes:
        
            if not solved:
    
                # Don't explore combinations that are fixed by basic sequencer
                if sequence012[step-1] == 1 and combi[0]==0: continue #try [1,1,1] and [1,0,1] only
                if sequence012[step-1] == 0 and combi[0]==1: continue #try [0,0,0] and [0,1,0] only
                            
                # Try solving for {step} hours
                sequence[f'combi{step}'] = combi
                cost, x_opt, u_opt, error = one_iteration(x_0, iter, sequence, 15*step, x_opt_prev, u_opt_prev)

                if step==1: print(f"\n******* combi1={combi} *******")

                if cost == 1e5:
                    print(f"{'-'*step} combi{step} = {combi} could not be solved: {error}")
                else:
                    solved = True
                    if step<8:
                        print(f"{'-'*step} combi{step} = {combi} is feasible. Testing for combi{step+1}:")
                    else:
                        print(f"Found a working sequence!\n{sequence}")
                        return sequence
                        print("#########################################")


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Save result in a CSV file
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# The name of the CSV file for the results
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
csv_file_name = "results_" + formatted_datetime + ".csv"

def append_to_csv(data, final_sequence):
    
    # Add the sequence to the data going to csv
    data[0]['sequence'] = [final_sequence[f'combi{i}'] for i in range(1,9)]
        
    with open(csv_file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["T_B", "T_S", "prices", "loads", "iter", "sequence"])
        
        # If file is empty, write headers
        if file.tell() == 0:
            writer.writeheader()
        
        # Append data to CSV
        for row in data:
            writer.writerow(row)
            
    print("Data was appended to", csv_file_name)
