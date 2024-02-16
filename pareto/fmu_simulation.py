import pandas as pd
import numpy as np
import csv
import time
import subprocess

PRINT = False

# Name of the FMU
fmuName = 'weiping_0CCC_0test_Examples_HP_0TES_0water_0test.fmu'
fmuNameNoSuffix = fmuName.replace(".fmu","")

# Get the FMU inputs for a given hour
def get_inputs(hour, delta_HP, T_sup_HP, weather):

    inputs_dict = {
        'T_closet': 273.15+30,
        'Tdcw': 273.15+12,
        'mdot_dcw': 0.2,
        'ResistanceThermalCapacity': 5000,
        'Resistance_On': False,
        'HP_mode': True,
        'T_OA': weather[hour] + 273,
        'TSupSet': T_sup_HP[hour] + 273,
        'HP_On': True if delta_HP[hour]==1 else False}
        
    return list(inputs_dict.values()), list(inputs_dict)

# Load the FMU and simulate the inputs
def simulate(delta_HP, T_sup_HP, weather, num_hours):

    # Simulation time frame (in seconds)
    start_time = 0
    final_time = (num_hours)*3600
    
    # Build the inputs (change every hour)
    inputs_array = []
    for hour in range(num_hours):
        current_time = hour*3600
        current_input, input_names = get_inputs(hour, delta_HP, T_sup_HP, weather)
        inputs_array.append([current_time]+current_input)
    # Duplicate the commands for the last hour
    inputs_array.append([current_time+3600]+current_input)
    inputs_array = np.array(inputs_array)
    
    # Final format for the FMU inputs
    inputs = (input_names, inputs_array)
    if PRINT: print(inputs)

    # Check that PyFMI is installed
    try:
        import pyfmi
        print("\nPyFMI is installed on this device.")
    except ImportError:
        print("\nPyFMI is not installed on this device.\n")
        return("")
    
    # Load FMU
    model = pyfmi.load_fmu(fmuName)
    print(f"Model {fmuName} was loaded.\n")

    # Simulate
    res = model.simulate(start_time=start_time, final_time=final_time, input=inputs)
    print(f"\nThe simulation has finished running on the FMU.")

    # Leave time to write .mat file
    time.sleep(1)

    # The simulation outputs a .mat file with results, convert it to csv.
    # The > print.txt just saves the prints from the script to another file.
    command = f"python mat_to_csv.py {fmuNameNoSuffix+'_result.mat'} > prints.txt"
    subprocess.call(command, shell=True)

    # Read the results file and save as csv
    results_dataframe = pd.read_csv(fmuNameNoSuffix+'_result.csv').drop('Unnamed: 0', axis=1)
    results_dataframe.to_csv('simulation_results.csv', index=False)
    print("Results saved in simulation_results.csv.\n")
    
    return results_dataframe
