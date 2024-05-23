import numpy as np
import matplotlib.pyplot as plt
import random
from functions import generic

# ---------------------------------------------------
# User inputs
# ---------------------------------------------------

constraints = {
    'storage_capacity': True,
    'max_storage': 20,
    'initial_soc': 0,

    'cheaper_hours': True,
    
    'low_noise': False,
    'low_noise_hours': [],
}

parameters = { 
    'horizon': 24,

    'elec_costs': [69.39, 64.75, 63.84, 63.31, 63.17, 63.17, 63.09, 395.85, 393.22, 398.68, 407.27, 407.75, 68.56, 
                   70.34, 74.25, 81.66, 413.34, 349.83, 349.82, 349.81, 6.73, 6.73, 6.74, 6.72],
    'loads': [5.8610651888228436, 5.718410471841691, 5.601993230462397, 5.718410471841691, 5.718410471841691, 
              6.002392694063915, 6.286494342809449, 6.286494342809449, 6.002392694063915, 5.718410471841691, 
              5.013683074581429, 5.013683074581429, 4.8563266008739525, 4.8563266008739525, 4.8563266008739525, 
              4.8563266008739525, 5.013683074581429, 5.013683074581429, 4.8563266008739525, 4.8563266008739525, 
              4.8563266008739525, 4.8563266008739525, 4.8563266008739525, 4.8563266008739525],
    
    'timestep': 'hourly',

    'control_max': [12]*24,
    'control_min_max_ratio': 0.5,
    'required_control': 0,

    'constraints': constraints
}

# ---------------------------------------------------
# Get costs per unit
# ---------------------------------------------------

# Get the costs per unit and treat for duplicates
costs_pu = parameters['elec_costs'].copy()

# Get rid of equal costs by adding a small random number
needs_check = True
while needs_check:
    needs_check = False
    for i in range(parameters['horizon']):
        for j in range(parameters['horizon']):
            if i!=j and costs_pu[i] == costs_pu[j]:
                costs_pu[j] = round(costs_pu[j] + random.uniform(-0.001, 0.001),4)
                needs_check = True

# ---------------------------------------------------
# Get the sequence
# ---------------------------------------------------

control = generic(parameters, costs_pu)
print(f"\nThe control sequence is:\n{control}\n")