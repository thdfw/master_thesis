from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from sklearn.metrics import mean_squared_error as rmse
import optimizer, functions, plot, forecasts, sequencer

# Set the DYMOLA_RUNTIME_LICENSE environment variable
license_path = r'c:/users/xiwang_lbl/appdata/roaming/dassaultsystemes/dymola/dymola.lic'
os.environ['DYMOLA_RUNTIME_LICENSE'] = license_path

# ------------------------------------------------------
# Define problem type (time step, horizon, etc.)
# ------------------------------------------------------

# Time step
delta_t_m = 4               # minutes
delta_t_h = delta_t_m/60    # hours
delta_t_s = delta_t_m*60    # seconds

# Integration method (euler, rk2, or rk4)
integration_method = 'rk4'

# Horizon (hours * time_steps/hour)
N = int(16 * 1/delta_t_h)

# Simulation time (hours)
simulation_time = 24

# FMU initialisation time (hours)
initialisation_time = 10

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          N,
'time_step':        delta_t_m,
'integration':      integration_method,
}

# Print corresponding setup
plot.print_pb_type(pb_type, simulation_time)

# ------------------------------------------------------
# Initialize
# ------------------------------------------------------

# Initial previous sequence
previous_sequence = {}
for i in range(8): previous_sequence[f'combi{i+1}'] = [1,1,1]

# Load previous sequence results from a csv file
file_path = input("\nResults file (enter to skip): ").replace(" ","")
print("No file selected.") if file_path=="" else print(f"Reading from {file_path.split('/')[-1]}.")

# For the results
rows = []
rows_pred = []

'''Remove and calculate at the end'''
# For the final plot
list_Q_HP = []
elec_cost, elec_used, heat_supp = 0, 0, 0
'''Remove and calculate at the end'''

# ------------------------------------------------------
# Get optimal inputs for the next hour
# ------------------------------------------------------

def get_inputs(iter, x_0, x_opt, u_opt):

    # Put x_0 in the same order as the rest of the code: T_B then T_S
    x_0 = x_0[-4:] + x_0[:-4]

    # ---------------------------------------------------
    # Solver warm start from previous iteration
    # ---------------------------------------------------
    
    # The last N-1 hours of the previous iteration
    initial_x = [[float(x) for x in x_opt[k,-(15*(int(N*delta_t_h)-1))-1:]] for k in range(16)]
    initial_u = [[float(u) for u in u_opt[k,-(15*(int(N*delta_t_h)-1)):]] for k in range(6)]
    
    # The last hour of the current iteration is not initialized
    initial_x = np.array([initial_x_i+[0]*15 for initial_x_i in initial_x])
    initial_u = np.array([initial_u_i+[0]*15 for initial_u_i in initial_u])
    
    # Packed in a dict that is given to the solver
    warm_start = {'initial_x': np.array(initial_x), 'initial_u': np.array(initial_u)}
    
    # ---------------------------------------------------
    # Find a sequence and solve the optimization problem
    # ---------------------------------------------------
    
    # As long as a feasible sequence is not found, try another method (attempt)
    attempt = 1
    obj_opt = 1e5
    previous_attempt = 0
    while obj_opt == 1e5:
        
        # Get a optimal sequence proposition from the MILP
        sequence, prev_attempt = sequencer.get_optimal_sequence(iter, previous_sequence, previous_attempt, file_path, attempt, x_0, pb_type)
                
        # Try to solve the optimization problem, get u* and x*
        u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, 15*iter, pb_type, sequence, warm_start, True)
        
        # Next attempt
        attempt += 1
        previous_attempt = prev_attempt
        
    # Save results in a csv file
    sequencer.append_to_csv(x_0, iter, sequence, pb_type)
    
    # Define the commands for the next hour
    m_stor = u_opt[1,:15]
    m_load = [forecasts.get_m_load(iter, iter+N, 1)[0] for _ in range(15)]
    T_sup_HP = u_opt[0,:15]
    delta_HP = u_opt[4,:15]
    
    # Put them in a dictionnary
    inputs_dict = {}
    for t in range(int(3600/delta_t_s)):
        inputs_dict[f'step_{t}'] = [m_stor[t], m_load[t], T_sup_HP[t], delta_HP[t]]
    
    return inputs_dict, x_opt, u_opt, sequence
    
# -------------------------------------------------------
# Initialize the FMU
# -------------------------------------------------------

# Extract the FMU file
fmu_path = 'fmu/plant_hp_fixed.fmu'
model_description = read_model_description(fmu_path)
unzipdir = extract(fmu_path)

# Read the inputs
vars_input = {}
for k in model_description.modelVariables:
    if k.causality == 'input':
        vars_input[k.name] = k.valueReference

# Read the outputs
vars_output = {}
for k in model_description.modelVariables:
    if k.causality == 'output':
        vars_output[k.name] = k.valueReference
        
# Remove unnecessary outputs
delete = ['CPUtime', 'EventCounter']
for k in delete:
    if k in vars_output.keys():
        del vars_output[k]

# Initializing the model
result = FMU2Slave(guid=model_description.guid,
                    unzipDirectory=unzipdir,
                    modelIdentifier=model_description.coSimulation.modelIdentifier)
result.instantiate()
result.setupExperiment(tolerance=1E-4, startTime=0.0)
result.enterInitializationMode()
result.exitInitializationMode()

# -------------------------------------------------------
# Initialize the FMU temperatures
# -------------------------------------------------------

# Read the initial state of the system
state = result.getReal(list(vars_output.values()))

# Define the initialisation commands
initialisation_commands = [0.15, 0.15, 310, 1]

# Run the FMU for the length of the initialisation (as one big step)
result.setReal(vars_input.values(), initialisation_commands)
result.doStep(currentCommunicationPoint=0, communicationStepSize=initialisation_time*3600)

# Read the new state, from which the simulation will start
rows.append(result.getReal(list(vars_output.values())))
print("\n-----------------------------------------------------")
print(f"FMU initialization ({initialisation_time} hours)")
print("-----------------------------------------------------\n")
print(f"State before initialization:\n{[round(x,1) for x in state]}")
state = rows[-1]
print(f"\nState after initialization:\n{[round(x,1) for x in state]}")

# -------------------------------------------------------
# Simulate the FMU
# -------------------------------------------------------

start_time = time.time()

# For each hour
for time_now in range(initialisation_time, initialisation_time+simulation_time):

    # The iteration in the simulation (after initialisation)
    iter = int(time_now-initialisation_time)

    # Initial solver warm start
    if iter == 0:
        old_u = np.zeros((6, N))
        old_x = np.zeros((16, N+1))
        
    # Read the optimal inputs for the next hour (lists of 15 elements)
    optimal_inputs, old_x, old_u, previous_sequence = get_inputs(iter, state, old_x, old_u)
    
    # To visualize the commands at every time step
    m_stor, m_load, T_sup_HP, delta_HP = [], [], [], []
    
    # Apply the inputs for the 15 elements to go to the next hour
    for k in range(int(3600/delta_t_s)):
        result.setReal(vars_input.values(), optimal_inputs[f'step_{k}'])
        result.doStep(currentCommunicationPoint=time_now*3600+k*delta_t_s, communicationStepSize=delta_t_s)
        rows.append(result.getReal(list(vars_output.values())))
        m_stor.append(round(optimal_inputs[f'step_{k}'][0],2))
        m_load.append(round(optimal_inputs[f'step_{k}'][1],2))
        T_sup_HP.append(round(optimal_inputs[f'step_{k}'][2],2))
        delta_HP.append(optimal_inputs[f'step_{k}'][3])
    
    # State predicted by equations during past hour
    state_pred = [[round(x,1) for x in old_x[k,:15]] for k in range(16)]
    state_pred = state_pred[4:] + state_pred[:4]
    state_pred = list(map(list, zip(*state_pred))) # transpose the list
    rows_pred.extend(state_pred)

    # PRINT State predicted by equations during past hour
    res_pred = pd.DataFrame(state_pred)
    res_pred.columns = vars_output.keys()
    res_pred['m_stor'], res_pred['m_load'], res_pred['T_sup_HP'], res_pred['delta_HP'] = m_stor, m_load, T_sup_HP, delta_HP
    print("\nPREDICTED Temperature evolution over the past hour:")
    print(res_pred)

    # PRINT State measured in FMU during past hour
    res = pd.DataFrame(rows[-16:-1], columns = vars_output.keys())
    res = res.round(1)
    res['m_stor'], res['m_load'], res['T_sup_HP'], res['delta_HP'] = m_stor, m_load, T_sup_HP, delta_HP
    print("\nREAL Temperature evolution over the past hour:")
    print(res)

    # Read the next state of the system (and increase to 308K if FMU went lower)
    for x in rows[-1]:
        if x<308:
            print("\nWARNING: The FMU finished with a temperature {x}K, which is below 308K, the minimum allowed.")
            print("Replaced with 308K to allow the next iteration to be feasible.\n")
    state = [308 if x<308 else x for x in rows[-1]]
    
    # Put x_0 in the same order as the rest of the code: T_B then T_S
    state_modif = state[-4:] + state[:-4]
    
    # Print iteration
    plot.print_iteration(old_u, old_x, state_modif, previous_sequence, 15*iter)
    
    # ------------------------------------------------------
    # Update and append values for final plot
    # ------------------------------------------------------

    # Get the Q_HP at evey time step over the next hour
    Q_HP_ = [functions.get_function("Q_HP", old_u[:,t], old_x[:,t], t, previous_sequence, 15*iter) for t in range(15)]
    Q_HP_ = [x/15 for x in Q_HP_]
    
    # Find the COP at evey time step over the next hour
    T_OA_, _, __ = forecasts.get_T_OA(15*iter, 15*(iter+1), delta_t_h)
    COP_ = [forecasts.get_COP(T_OA_[t], old_u[0,t]) for t in range(15)]
    
    # Get the electricty used and the cost of electricity over the next hour
    for k in range(15):
        heat_supp += Q_HP_[k]
        elec_used += Q_HP_[k] / COP_[k]
        elec_cost += Q_HP_[k] / COP_[k] * forecasts.get_c_el(15*iter, 15*iter+1, delta_t_h)[0]

    # Append Q_HP values for the next hour (for plot)
    list_Q_HP.extend([functions.get_function("Q_HP", old_u[:,t], old_x[:,t], 0, previous_sequence, 15*iter) for t in range(15)])

# Terminate
result.terminate()
result.freeInstance()

# ------------------------------------------------------
# Gather all the data from the simulation
# ------------------------------------------------------

res = pd.DataFrame(rows, columns = vars_output.keys())
res = res.round(1)
print("\nSimulation results:")
print(res)
list_B1, list_B2, list_B3, list_B4 = list(res['T[13]']), list(res['T[14]']), list(res['T[15]']), list(res['T[16]'])
list_S11, list_S12, list_S13, list_S14 = list(res['T[1]']), list(res['T[2]']), list(res['T[3]']), list(res['T[4]'])
list_S21, list_S22, list_S23, list_S24 = list(res['T[5]']), list(res['T[6]']), list(res['T[7]']), list(res['T[8]'])
list_S31, list_S32, list_S33, list_S34 = list(res['T[9]']), list(res['T[10]']), list(res['T[11]']), list(res['T[12]'])

# ------------------------------------------------------
# Gather all data from the prediction
# ------------------------------------------------------

res_pred = pd.DataFrame(rows_pred)
res_pred.columns = vars_output.keys()
res_pred = res_pred.round(1)
print("\nPrediction results:")
print(res_pred)
list_B1_pred, list_B2_pred, list_B3_pred, list_B4_pred =\
 list(res_pred['T[13]']), list(res_pred['T[14]']), list(res_pred['T[15]']), list(res_pred['T[16]'])
list_S11_pred, list_S12_pred, list_S13_pred, list_S14_pred =\
 list(res_pred['T[1]']), list(res_pred['T[2]']), list(res_pred['T[3]']), list(res_pred['T[4]'])
list_S21_pred, list_S22_pred, list_S23_pred, list_S24_pred =\
 list(res_pred['T[5]']), list(res_pred['T[6]']), list(res_pred['T[7]']), list(res_pred['T[8]'])
list_S31_pred, list_S32_pred, list_S33_pred, list_S34_pred =\
 list(res_pred['T[9]']), list(res_pred['T[10]']), list(res_pred['T[11]']), list(res_pred['T[12]'])

# Print total simulation time
total_time = time.time()-start_time
hours = round(total_time // 3600)
minutes = round((total_time % 3600) // 60)
print(f"\nThe {simulation_time}-hour simulation ran in {hours} hour(s) and {minutes} minute(s).")

# ------------------------------------------------------
# Plot difference between simulation and prediction
# ------------------------------------------------------

plt.plot(list_B1, color='tab:blue', label='FMU')
plt.plot(list_B1_pred, color='tab:orange', label='Prediction')
#plt.plot(list_B2, color='tab:blue')
#plt.plot(list_B2_pred, color='tab:orange')
#plt.plot(list_B3, color='tab:blue')
#plt.plot(list_B3_pred, color='tab:orange')
plt.plot(list_B4, color='tab:blue')
plt.plot(list_B4_pred, color='tab:orange')
plt.title("Temperatures of the top and bottom of the buffer tank")
plt.xlabel("Iterations")
plt.ylabel("Temperature [K]")
plt.ylim([305,335])
plt.legend()
plt.show()

plt.plot(list_S11, color='tab:blue', label='FMU')
plt.plot(list_S11_pred, color='tab:orange', label='Prediction',)
#plt.plot(list_S12, color='tab:blue')
#plt.plot(list_S12_pred, color='tab:orange')
#plt.plot(list_S13, color='tab:blue')
#plt.plot(list_S13_pred, color='tab:orange')
plt.plot(list_S14, color='tab:blue')
plt.plot(list_S14_pred, color='tab:orange')
plt.title("Temperatures of the top and bottom of storage tank 1")
plt.xlabel("Iterations")
plt.ylabel("Temperature [K]")
plt.ylim([305,335])
plt.legend()
plt.show()

plt.plot(list_S21, color='tab:blue', label='FMU')
plt.plot(list_S21_pred, color='tab:orange', label='Prediction',)
#plt.plot(list_S22, color='tab:blue')
#plt.plot(list_S22_pred, color='tab:orange')
#plt.plot(list_S23, color='tab:blue')
#plt.plot(list_S23_pred, color='tab:orange')
plt.plot(list_S24, color='tab:blue')
plt.plot(list_S24_pred, color='tab:orange')
plt.title("Temperatures of the top and bottom of storage tank 2")
plt.xlabel("Iterations")
plt.ylabel("Temperature [K]")
plt.ylim([305,335])
plt.legend()
plt.show()

plt.plot(list_S31, color='tab:blue', label='FMU')
plt.plot(list_S31_pred, color='tab:orange', label='Prediction',)
#plt.plot(list_S32, color='tab:blue')
#plt.plot(list_S32_pred, color='tab:orange')
#plt.plot(list_S33, color='tab:blue')
#plt.plot(list_S33_pred, color='tab:orange')
#plt.plot(list_S34, color='tab:blue')
plt.plot(list_S34_pred, color='tab:orange')
plt.title("Temperatures of the top and bottom of storage tank 3")
plt.xlabel("Iterations")
plt.ylabel("Temperature [K]")
plt.ylim([305,335])
plt.legend()
plt.show()

# ------------------------------------------------------
# Compute the total error of the prediction
# ------------------------------------------------------

total_rmse = 0

# Buffer
total_rmse += rmse(list_B1[:-1], list_B1_pred, squared=True)
total_rmse += rmse(list_B2[:-1], list_B2_pred, squared=True)
total_rmse += rmse(list_B3[:-1], list_B3_pred, squared=True)
total_rmse += rmse(list_B4[:-1], list_B4_pred, squared=True)

# Storage
total_rmse += rmse(list_S11[:-1], list_S11_pred, squared=True)
total_rmse += rmse(list_S12[:-1], list_S12_pred, squared=True)
total_rmse += rmse(list_S13[:-1], list_S13_pred, squared=True)
total_rmse += rmse(list_S14[:-1], list_S14_pred, squared=True)
total_rmse += rmse(list_S21[:-1], list_S21_pred, squared=True)
total_rmse += rmse(list_S22[:-1], list_S22_pred, squared=True)
total_rmse += rmse(list_S23[:-1], list_S23_pred, squared=True)
total_rmse += rmse(list_S24[:-1], list_S24_pred, squared=True)
total_rmse += rmse(list_S31[:-1], list_S31_pred, squared=True)
total_rmse += rmse(list_S32[:-1], list_S32_pred, squared=True)
total_rmse += rmse(list_S33[:-1], list_S33_pred, squared=True)
total_rmse += rmse(list_S34[:-1], list_S34_pred, squared=True)

total_rmse = np.sqrt(total_rmse)

print(f"\nThe total RMSE over the simulation is {total_rmse} [K].")

# ------------------------------------------------------
# Final prints and plot
# ------------------------------------------------------

# Regroup plot data
plot_data = {
    'pb_type':      pb_type,
    'iterations':   simulation_time,
    'c_el':         forecasts.get_c_el(0, 15*simulation_time, delta_t_h),
    'm_load':       forecasts.get_m_load(0, 15*simulation_time, delta_t_h),
    'Q_HP':         list_Q_HP,
    'T_S11':        list_S11,
    'T_S12':        list_S12,
    'T_S13':        list_S13,
    'T_S14':        list_S14,
    'T_S21':        list_S21,
    'T_S22':        list_S22,
    'T_S23':        list_S23,
    'T_S24':        list_S24,
    'T_S31':        list_S31,
    'T_S32':        list_S32,
    'T_S33':        list_S33,
    'T_S34':        list_S34,
    'T_B1':         list_B1,
    'T_B2':         list_B2,
    'T_B3':         list_B3,
    'T_B4':         list_B4,
    'T_S11_pred':   list_S11_pred,
    'T_S21_pred':   list_S21_pred,
    'T_S31_pred':   list_S31_pred,
    'T_B1_pred':    list_B1_pred,
    'T_B4_pred':    list_B4_pred,
    'elec_cost':    round(elec_cost,2),
    'elec_used':    round(elec_used/1000,2),
    'heat_supp':    round(heat_supp/1000,2),
}

print("\nPlotting the data...\n")
plot.plot_MPC(plot_data, True, True)
plot.plot_MPC(plot_data, True, False)