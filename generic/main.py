'''Code for generic control algorithm'''
print("")

import numpy as np
import matplotlib.pyplot as plt
import random
from functions import turn_on, get_status, get_storage, iteration_plot, compute_costs

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
    'elec_costs': [69.39, 64.75, 63.84, 63.31, 63.17, 63.17, 
                   63.09, 395.85, 393.22, 398.68, 407.27, 407.75, 68.56, 
                   70.34, 74.25, 81.66, 413.34, 349.83, 349.82, 349.81, 6.73, 
                   6.73, 6.74, 6.72],
    'loads': [5.8610651888228436, 5.718410471841691, 5.601993230462397, 5.718410471841691, 5.718410471841691, 
              6.002392694063915, 6.286494342809449, 6.286494342809449, 6.002392694063915, 5.718410471841691, 
              5.013683074581429, 5.013683074581429, 4.8563266008739525, 4.8563266008739525, 4.8563266008739525, 
              4.8563266008739525, 5.013683074581429, 5.013683074581429, 4.8563266008739525, 4.8563266008739525, 
              4.8563266008739525, 4.8563266008739525, 4.8563266008739525, 4.8563266008739525],
    'horizon': 24,
    'timestep': 'hourly',
    'control_max': [12]*24,
    'control_min_max_ratio': 0.5,
    'required_control': 0,
    'constraints': constraints
}

# Extracting some parameters
N = parameters['horizon']

# Get the costs per unit and treat for duplicates
costs_pu = parameters['elec_costs'].copy()

# Get rid of equal costs by adding a small random number
needs_check = True
while needs_check:
    needs_check = False
    for i in range(N):
        for j in range(N):
            if i!=j and costs_pu[i] == costs_pu[j]:
                costs_pu[j] = round(costs_pu[j] + random.uniform(-0.001, 0.001),4)
                needs_check = True

# ---------------------------------------------------
# Initialize
# ---------------------------------------------------

# Control variable
control = [0]*N
control_max = parameters['control_max']

# Hours ranked by price
hours_ranked = [costs_pu.index(x) for x in sorted(costs_pu)]

# Status list
if parameters['timestep'] == 'hourly':
    status = [1]*N
elif parameters['timestep'] == 'daily':
    status = [0]*(N-1) + [1]

# ---------------------------------------------------
# Run the generic algorithm
# ---------------------------------------------------

# While all hours are not satisfied
while sum(status) > 0:

    # Find the next unsatisfied hour
    next_not_ok = status.index(1)
    print("\n---------------------------------------")
    print(f"The next unsatisfied hour: {next_not_ok}:00")
    print("---------------------------------------")

    # Find and turn on the cheapest remaining hour(s) before it, until it is satisfied
    for hour in hours_ranked:
        
        # Skip hours that are after the next unsatisfied hour
        if hour > next_not_ok: 
            continue

        # Skip hours which are already used to their maximum
        if control[hour] == control_max[hour]: 
            continue

        # Skip hours before a maximum storage occurence
        if parameters['constraints']['storage_capacity']:
            storage_full = [1 if round(x,1)==parameters['constraints']['max_storage'] else 0 for x in get_storage(control, parameters)]
            if sum(storage_full)>0 and hour <= storage_full.index(1):
                continue
        
        print(f"\nThe cheapest remaining hour before {next_not_ok}:00 is {hour}:00.")

        # Turn on the equipment with constraints in mind, eventually update maximum
        control[hour], control_max[hour] = turn_on(hour, control, control_max, parameters, next_not_ok)

        # Update the status vector
        status = get_status(control, parameters)
        
        # Check implications and plot
        if sum(status) == 0:
            print("\n" + "*"*30 + "\nProblem solved!\n" + "*"*30 + "\n")            
            compute_costs(control, parameters)
            iteration_plot(control, parameters)
            break

        if next_not_ok != status.index(1):
            print(f"\nSatisfied hour {next_not_ok}:00, now next not ok is {status.index(1)}:00.\n")
            #iteration_plot(control, parameters)
            next_not_ok = status.index(1)
            break

print("\n")