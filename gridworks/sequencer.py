import numpy as np
import matplotlib.pyplot as plt

def get_sequence(c_el, m_load, hour):

    PLOT = False
    result = 2*np.ones(len(c_el))
        
    for i in range(len(c_el)):

        # Turn off the heat pump in high price periods
        if c_el[i] > 20: result[i] = 0

        # Turn on the heat pump in negative price periods
        if c_el[i] < 0: result[i] = 1

        # Detect peaks, and their length
        if i<(len(c_el)-1) and abs(c_el[i+1] - c_el[i]) >= 15:
            if c_el[i+1] - c_el[i] > 0 and c_el[i+1]>20:
                length = i
                #print(f"Price peak starting at {i+1}h")
            if c_el[i+1] - c_el[i] < 0  and c_el[i]>20:
                length = i - length
                #print(f"Price peak finishing at {i+1}h, after {length} hours\n")

                # Find number of hours to charge before each peak depending on load
                if round(np.mean(m_load),2) >= 0.1:
                    hours_charge = length
                    title = "High load"
                elif round(np.mean(m_load),2) >= 0.05:
                    hours_charge = int(round(length/2 + 0.001)) if length>=2 else 1
                    title = "Medium load"
                else:
                    hours_charge = int(round(length/3 + 0.001)) if length>=3 else 1
                    title = "Low load"

                # Charge the tanks for as long as necessary before the peak
                for j in range(hours_charge):
                    if result[i-length-j] == 2:
                        result[i-length-j] = 1

    # Get the indices of the hours in which two options are possible
    two_option_indices = [1 if x==2 else np.nan for x in result]

    # If now is an undetermined state, try running one hour off
    if result[hour] == 2: result[hour] = 0
        
    # All others are seen as on for now
    result = [1 if x==2 else int(x) for x in result]

    if PLOT:
        
        # Replace past hours by NaN
        c_el_final = [np.nan]*hour + c_el[hour:]
        result_final = [np.nan]*hour + result[hour:]
        two_option_indices_final = [np.nan]*hour + two_option_indices[hour:]
        
        # Plot the results
        fig, ax = plt.subplots(1,1, figsize=(12,4), sharex=True)
        ax.step(range(len(c_el)), c_el_final, where='post', alpha=0.4, color='black')
        ax.set_xticks(range(len(c_el)))
        ax.set_xlim([-1,len(c_el)])
        ax.set_ylim([0,50])
        ax2 = ax.twinx()
        ax2.step(range(len(c_el)), result_final, where='post', color='blue', alpha=0.4)
        ax2.step(range(len(c_el)), two_option_indices_final, where='post', color='red', alpha=0.9)
        ax2.set_yticks(range(3))
        if two_option_indices[hour] == 1: title += " - check both options"
        plt.axvline(x=hour+8, color='green', linestyle='dashed',alpha=0.1)
        plt.axvspan(hour, hour+8, facecolor='green', alpha=0.05, label='Highlight')
        plt.title(f"{title}")
        plt.show()

    # The 8-hour trim
    hour8_trim = result[hour:] + [1] * hour
    hour8_trim = hour8_trim[:8]
    
    # Convert
    hour8_trim = [[1,1,1] if x==1 else [0,0,0] for x in hour8_trim]
    final_dict = {}
    for i in range(len(hour8_trim)):
        final_dict[f'combi{i+1}'] = hour8_trim[i]
        
    # Check if yes or no there are two options
    test_2_options = two_option_indices[hour] == 1

    return final_dict, test_2_options
