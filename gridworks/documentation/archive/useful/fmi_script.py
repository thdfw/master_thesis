# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 18:41:04 2024

@author: remi
"""

from fmpy import read_model_description, dump, extract 
from fmpy.fmi2 import FMU2Slave
import pandas as pd
import os


# # Set the DYMOLA_RUNTIME_LICENSE environment variable

# license_path = r'c:/users/xiwang_lbl/appdata/roaming/dassaultsystemes/dymola/dymola.lic'
# os.environ['DYMOLA_RUNTIME_LICENSE'] = license_path


# Read the FMU

fmu = r'C:\git\plant_hp_variable.fmu'
model_description = read_model_description(fmu)
unzipdir = extract(fmu)

# Read the inputs and outputs from the FMU
# To be noted, in this stage we creat a dictionary with the names of the inputs 
# and the corresponding "address" or "ID" in the FMU

vars_input = {}
for k in model_description.modelVariables: 
    if k.causality == 'input':
        vars_input[k.name] = k.valueReference

vars_output = {}
for k in model_description.modelVariables: 
    if k.causality == 'output':
        vars_output[k.name] = k.valueReference

# Optional output that are not useful (maybe for debug ?) and that may be also 
# not in the FMU if the correct option is selected at the export stage of the FMU

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
step = 100
rows = []
while time < 2000:
    result.setReal(vars_input.values(), [0.1, 0.2, 60 + 273.15, 1 if time < 1000 else 0])
    rows.append(result.getReal(list(vars_output.values())))
    result.doStep(currentCommunicationPoint=time, communicationStepSize=step)
    time = time + step
    
# end of the execution

rows.append(result.getReal(list(vars_output.values())))
result.terminate()
result.freeInstance()

res = pd.DataFrame(rows, columns = vars_output.keys())


