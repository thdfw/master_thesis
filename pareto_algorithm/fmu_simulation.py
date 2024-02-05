import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import csv
import time

PRINT = False

# Name of the FMU
fmuName = 'fmu_name_here.fmu'
fmuNameNoSuffix = fmuName.replace(".fmu","")

# Get the FMU inputs for a given hour
def get_inputs(hour, delta_HP, T_sup_HP, weather):
    
    inputs_dict = {
        # Pareto inputs, change at every hour
        'HP_On': delta_HP[hour],
        'TSupSet': T_sup_HP[hour],
        'T_OA': weather[hour],
        # Other inputs
        'T_closet': 273.15+30,
        'Tdcw': 273.15+12,
        'mdot_dcw': 0.2,
        'ResistanceThermalCapacity': 5000,
        'Resistance_On': True,
        'HP_mode': True}
        
    return list(inputs_dict.values()), list(inputs_dict)

# Load the FMU and simulate the inputs
def simulate(delta_HP, T_sup_HP, weather, num_days):
    
    # Build the inputs (change every hour)
    inputs_array = []
    for hour in range(24*num_days):
        current_time = hour*3600
        current_input, input_names = get_inputs(hour, delta_HP, T_sup_HP, weather)
        inputs_array.append([current_time]+current_input)
    inputs_array = np.array(inputs_array)
    
    # Final format for the FMU inputs
    inputs = (input_names, inputs_array)
    
    # Check that PyFMI is installed
    try:
        import pyfmi
        if PRNIT: print("\nPyFMI is installed on this device.")
    except ImportError:
        print("\nPyFMI is not installed on this device.\n")
        return("")
    
    # Load FMU and simulate
    model = pyfmi.load_fmu(fmuName)
    res = model.simulate(start_time=start_time, final_time=final_time, input=inputs)
    if PRINT: print(f"\nThe simulation has been run on the FMU.")

    # If necessary
    time.sleep(1)

    # The simulation outputs a .mat file with results, convert to csv.
    # The > print.txt just saves the prints from the script to another file.
    command = f"python mat_to_csv.py {fmuNameNoSuffix+'_result.mat'} > prints.txt"
    subprocess.call(command, shell=True)

    # Read the results file
    results_dataframe = pd.read_csv(fmuNameNoSuffix+'_result.csv').drop('Unnamed: 0', axis=1)
    
    return results_dataframe
