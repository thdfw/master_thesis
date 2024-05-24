import pandas as pd
import numpy as np
import csv
import time
import subprocess

PRINT = False

# Name of the FMU
fmuName = 'R32HpTesTest_parallel.fmu'
fmuNameNoSuffix = fmuName.replace(".fmu","")

# Check that PyFMI is installed
try:
    import pyfmi
    if PRINT: print("\nPyFMI is installed on this device.")
except ImportError:
    print("\nPyFMI is not installed on this device.\n")

# Load FMU
model = pyfmi.load_fmu(fmuName)
if PRINT: print(f"Model {fmuName} was loaded.\n")

def m_HP(T):
    if   T<=45: m = 34.5/60
    elif T<=55: m = 21.6/60 #(0.36 kg/s)
    else:       m = 17.3/60 #(0.29 kg/s)
    return round(m,2)

# Get the FMU inputs for a given hour
def get_inputs(min, commands, weather):

    weather = [x for x in weather for _ in range(60)]

    inputs_dict = {
        'SysMode': commands['mode'][min],
        'HeatPumpWaterSupplyMassFlow': 0.29,
        'HeatPumpOnOff': commands['delta_HP'][min],
        'HeatPumpMode': 1,
        'HeatPumpWaterTempSetpoint': commands['T_sup_HP'][min] + 273,
        'OutdoorAirTemperature': weather[min] + 273,
        'ZoneHeatingLoad': commands['load'][min]*1000,
    }
        
    return list(inputs_dict.values()), list(inputs_dict)

# Load the FMU and simulate the inputs
def simulate(commands, weather, num_hours, iter):

    # Simulation time frame (in seconds)
    start_time = 0
    final_time = (num_hours)*3600
    
    # Build the inputs (change every hour)
    inputs_array = []
    for hour in range(num_hours):
        for minute in range(0,60):
            current_time = hour*3600 + minute*60
            current_input, input_names = get_inputs(minute, commands, weather)
            inputs_array.append([current_time]+current_input)
    # Duplicate the commands for the last hour
    inputs_array.append([current_time+3600]+current_input)
    inputs_array = np.array(inputs_array)
    
    opts = model.simulate_options()
    
    if iter==0:
        opts["ncp"] = 60
    else:
        state = model.get_fmu_state()
        opts['initialize'] = False
        opts["ncp"] = 60
        model.set_fmu_state(state)
    
    # Final format for the FMU inputs
    inputs = (input_names, inputs_array)
    if PRINT: print(inputs)

    # Simulate
    res = model.simulate(start_time=start_time, final_time=final_time, input=inputs, options=opts)
    if PRINT: print(f"\nThe simulation has finished running on the FMU.")

    # Leave time to write .mat file
    time.sleep(1)

    # The simulation outputs a .mat file with results, convert it to csv.
    # The > print.txt just saves the prints from the script to another file.
    command = f"python mat_to_csv.py {fmuNameNoSuffix+'_result.mat'} > prints.txt"
    subprocess.call(command, shell=True)
    if PRINT: print("Converted the .mat results to .csv")

    # Read the results file and save as csv
    results_dataframe = pd.read_csv(fmuNameNoSuffix+'_result.csv').drop('Unnamed: 0', axis=1)
    results_dataframe.to_csv('simulation_results.csv', index=False)
    if PRINT: print("Results saved in simulation_results.csv.\n")
    print(results_dataframe)
    
    return results_dataframe
