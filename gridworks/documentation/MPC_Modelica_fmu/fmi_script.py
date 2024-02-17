from fmpy import read_model_description, dump, extract
from fmpy.fmi2 import FMU2Slave
import pandas as pd

# Get the commands for the hour
def get_commands(x_0):
    m_stor = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    m_load = [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11]
    T_sup_HP = [311.77, 311.77, 311.77, 311.77, 312.62, 313.19, 313.42, 313.5, 313.94, 314.49, 314.9, 315.13, 315.43, 315.87, 316.32]
    delta_HP = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    return m_stor, m_load, T_sup_HP, delta_HP

# Get the commands per time step
def get_inputs(time, current_state):
    
    # Initialisation to get the desired initial state
    if time<7200:
        inputs_list = [0, 0, 310, 1]
    # The actual commands
    else:
        # HERE IS WHERE YOU GET THE COMMANDS BASED ON THE CURRENT STATES => CALL MPC
        m_stor, m_load, T_sup_HP, delta_HP = get_commands(current_state)
        t = int((time-7200)/4/60)
        inputs_list = [m_stor[t], m_load[t], T_sup_HP[t], delta_HP[t]]
        print(f"{t}: {inputs_list}")
    #print(f"Input at {int(time/60)} min: \n{inputs_list}: ")
    
    return inputs_list

# Extract the FMU
fmu = 'plant_hp_fixed_2023.fmu'
model_description = read_model_description(fmu)
unzipdir = extract(fmu)

vars_input = {}
for k in model_description.modelVariables:
    if k.causality == 'input':
        vars_input[k.name] = k.valueReference

vars_output = {}
for k in model_description.modelVariables:
    if k.causality == 'output':
        vars_output[k.name] = k.valueReference
        
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

# Executing the FMU
# To modify the input, we use the function
# result.setReal([list of adresses of the inputs], [list of values for those adddresses])

time = 0
step = 240 # 4 min time steps
rows = []
rows.append(result.getReal(list(vars_output.values())))
state = rows[-1]

while time < 3*3600: # 1 hour with 2 hour initialisation
    result.setReal(vars_input.values(), get_inputs(time, state))
    result.doStep(currentCommunicationPoint=time, communicationStepSize=step)
    rows.append(result.getReal(list(vars_output.values())))
    state = rows[-1]
    time = time + step
    
# Terminate
result.terminate()
result.freeInstance()

# Read final state and print results
res = pd.DataFrame(rows, columns = vars_output.keys())
print(res[['T[13]','T[14]','T[15]','T[16]']].loc[30:])
