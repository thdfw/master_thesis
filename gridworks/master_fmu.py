from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import pandas as pd
import numpy as np
import optimizer, functions, plot, forecasts, sequencer

# ------------------------------------------------------
# Define problem type (time step, horizon, etc.)
# ------------------------------------------------------

# Time step
delta_t_m = 4               # minutes
delta_t_h = delta_t_m/60    # hours
delta_t_s = delta_t_m*60    # seconds

# Horizon (hours * time_steps/hour)
N = int(8 * 1/delta_t_h)

# Simulation time (hours)
simulation_time = 4

# FMU initialisation time (hours)
initialisation_time = 10

# Problem type
pb_type = {
'linearized':       False,
'mixed-integer':    False,
'gurobi':           False,
'horizon':          N,
'time_step':        delta_t_m,
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

    # Prepare package for possible long sequence search function
    long_seq_pack = {'x_0': x_0, 'x_opt_prev': x_opt, 'u_opt_prev': u_opt}
    
    # As long as a feasible sequence is not found, try another method (attempt)
    attempt = 1
    obj_opt = 1e5
    while obj_opt == 1e5:
        
        # Get a good sequence proposition (method depends on attempt)
        sequence = sequencer.get_optimal_sequence(iter, previous_sequence, file_path, attempt, long_seq_pack, pb_type)
        
        # Try to solve the optimization problem, get u* and x*
        u_opt, x_opt, obj_opt, error = optimizer.optimize_N_steps(x_0, 15*iter, pb_type, sequence, warm_start, True)
        
        # Next attempt
        attempt += 1
        
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
fmu_path = 'fmu/plant_hp_fixed_2023.fmu'
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

# Initial state
rows = []
rows.append(result.getReal(list(vars_output.values())))

# -------------------------------------------------------
# Initialize the FMU temperatures
# -------------------------------------------------------

# Read the initial state of the system
state = rows[-1]

# Define the initialisation commands
initialisation_commands = [0.15, 0.15, 310, 1]

# Run the FMU for the length of the initialisation (as one big step)
result.setReal(vars_input.values(), initialisation_commands)
result.doStep(currentCommunicationPoint=0, communicationStepSize=initialisation_time*3600)

# Read the new state, from which the simulation will start
rows.append(result.getReal(list(vars_output.values())))
print("\n--------------------------------")
print(f"Initialization ({initialisation_time} hours)")
print("--------------------------------\n")
print(f"State before initialization:\n{[round(x,1) for x in state]}")
state = rows[-1]
print(f"\nState after initialization:\n{[round(x,1) for x in state]}")

# -------------------------------------------------------
# Simulate the FMU
# -------------------------------------------------------

# For each hour
for time in range(initialisation_time, initialisation_time+simulation_time):

    # The iteration in the simulation (after initialisation)
    iter = int(time-initialisation_time)

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
        result.doStep(currentCommunicationPoint=time*3600+k*delta_t_s, communicationStepSize=delta_t_s)
        rows.append(result.getReal(list(vars_output.values())))
        m_stor.append(round(optimal_inputs[f'step_{k}'][0],2))
        m_load.append(round(optimal_inputs[f'step_{k}'][1],2))
        T_sup_HP.append(round(optimal_inputs[f'step_{k}'][2],2))
        delta_HP.append(optimal_inputs[f'step_{k}'][3])
    
    # We do not give inputs for the last state
    m_stor.append(np.nan)
    m_load.append(np.nan)
    T_sup_HP.append(np.nan)
    delta_HP.append(np.nan)

    # Show the evolution of the state during the past hour
    res = pd.DataFrame(rows[-16:], columns = vars_output.keys())
    res = res.round(1)
    res = res[['T[13]','T[14]','T[15]','T[16]']]
    res['m_stor'], res['m_load'], res['T_sup_HP'], res['delta_HP'] = m_stor, m_load, T_sup_HP, delta_HP
    print("\nTemperature evolution over the past hour:")
    print(res)

    # Read the next state of the system
    print(f"\nInitial state:\n{[round(x,1) for x in state]}")
    state = rows[-1]
    print(f"\nNext state:\n{[round(x,1) for x in state]}")
    
    # Print iteration
    # Put x_0 in the same order as the rest of the code: T_B then T_S
    state_modif = state[-4:] + state[:-4]
    plot.print_iteration(old_u, old_x, state_modif, previous_sequence, 15*iter)

# Terminate
result.terminate()
result.freeInstance()

# Gather all the data from the simulation
res = pd.DataFrame(rows, columns = vars_output.keys())
res = res.round(1)
#print('\nThe final results:')
#print(res[['T[13]','T[14]','T[15]','T[16]']])
