import numpy as np
import matplotlib.pyplot as plt

def get_sequence(c_el, m_load, hour, previous_sequence):

    PLOT, PRINT = False, False
    
    # Initialize the sequence with 2s (0=off, 1=on, 2=undetermined)
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
                    hours_charge = int(round(length/3 + 0.001)) if length>=3 else 1

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
    sequence_trimmed = sequence[hour:] + [1] * hour
    sequence_trimmed = sequence_trimmed[:8]
    
    # Convert to combination format
    sequence_trimmed = [[1,1,1] if x==1 else [0,0,0] for x in sequence_trimmed]
    sequence_dict = {}
    for i in range(len(sequence_trimmed)):
        sequence_dict[f'combi{i+1}'] = sequence_trimmed[i]

    # Report if there are two options (current mode is undetermined)
    undertermined_now = two_option_indices[hour] == 1
    
    print("Previous sequence:\n", previous_sequence)
    print("Current sequence before comparison:\n", sequence_dict)
    for i in range(1,9):
        # If there is a [0,0,0] -> [0,1,0] change in previous sequence
        if i<8 and sequence_dict[f'combi{i}'] == [0,0,0] and previous_sequence[f'combi{i+1}'] == [0,1,0]:
            sequence_dict[f'combi{i}'] = [0,1,0]
            print(f"Replaced [0,0,0] with [0,1,0] in combi{i}")
        # If there is a [1,1,1] -> [1,0,1] change in previous sequence
        if i<8 and sequence_dict[f'combi{i}'] == [1,1,1] and previous_sequence[f'combi{i+1}'] == [1,0,1]:
            sequence_dict[f'combi{i}'] = [1,0,1]
            print(f"Replaced [1,1,1] with [1,0,1] in combi{i}")
    
    return sequence_dict, undertermined_now
