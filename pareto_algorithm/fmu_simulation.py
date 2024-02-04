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

def simulate(delta_HP, T_sup_HP, weather):

    # Check that PyFMI is installed
    try:
        import pyfmi
        if PRNIT: print("\nPyFMI is installed on this device.")
    except ImportError:
        print("\nPyFMI is not installed on this device.\n")
        return("")
    
    # Simulation time in seconds (1 hour)
    start_time = 0
    final_time = 3600
    
    # Inputs to the FMU
    inputs_dict = {
    
        # Pareto inputs, change at every hour
        'HP_On': delta_HP,
        'TSupSet': T_HP,
        'T_OA': weather,
    
        # Other inputs
        'T_closet': 273.15+30,
        'Tdcw': 273.15+12,
        'mdot_dcw': 0.2,
        'ResistanceThermalCapacity': 5000,
        'Resistance_On': True,
        'HP_mode': True}
    
    # Final format for the FMU inputs
    inputs = (
        list(inputs_dict),
        # In this case the inputs are constant during the entire simulation
        np.array(
            [[start_time]+list(inputs_dict.values()),
             [final_time]+list(inputs_dict.values())]))
    
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
