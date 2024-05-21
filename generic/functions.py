import matplotlib.pyplot as plt

'''
Turns on the system during the cheapest hour
While making sure no constraints are violated
'''
def turn_on(hour, control, control_max, parameters, next_not_ok):

    # Backup
    control_backup = control.copy()

    # TODO: make the 0.3 a user input / parameter
    control_min = [x*parameters['control_min_max_ratio'] for x in control_max]

    # Start with applying max power or cheapest mode
    if parameters['timestep'] == 'hourly':
        print(f"Try the maximum: {control_max[hour]}")
        control[hour] = control_max[hour]
    if parameters['timestep'] == 'daily':
        print("Turn on cheapest mode")

    # Check all activated constraints
    for key, value in parameters['constraints'].items():
        if value:

            # ----------------------------
            # Maximum storage capacity
            # ----------------------------

            if key == "storage_capacity":
                print("\n[Constraint] Check the storage capacity is not exceeded, if not reduce power")

                storage = [parameters['constraints']['initial_soc']] + [0]*parameters['horizon']
                max_storage = parameters['constraints']['max_storage']
                
                # Count the amount of storage excess
                storage_excess = round(max([x-max_storage if x-max_storage>0 else 0 for x in get_storage(control, parameters)]),1)

                # If there is no excess, stick to maximum
                if storage_excess == 0:
                    print(f"[DONE] We can use the maximum power at this hour.")

                else:
                    print(f"We need to use {storage_excess} less kW than the maximum.")
                
                    # See if you can reduce the power at that time
                    if control[hour] - storage_excess > control_min[hour]:
                        print("[DONE] That is feasible.")
                        # Set the control to the max power that does not exceed storage
                        control[hour] += -storage_excess
                        # Update the maximum
                        control_max[hour] = control_max[hour] - storage_excess

                    # If not, keep at same power
                    else:
                        print(f"[DONE] Infeasible, keeped at current power {control_backup[hour]}.\n")
                        control[hour] = control_backup[hour]

            # ----------------------------
            # Reaching cheaper hours
            # ----------------------------

            if key == "cheaper_hours":

                # Check the new current status
                status = get_status(control, parameters)

                # If the problem is not solved yet and the next unsatisfied hour has been satisfied
                if (sum(status) > 0 
                    and status.index(1) != next_not_ok 
                    and control[hour] > control_min[hour]):

                    costs = parameters['elec_costs']

                    # Check if a cheaper price has been passed while reaching the new next unsatisfied hour
                    if min(costs[next_not_ok:status.index(1)+1]) < costs[hour]:
                        print(f"\n[Constraint] Another hour on the way to the new next unsatisfied hour ({status.index(1)}:00) is cheaper than now.")

                        # Find the first hour in that section that is cheaper than the current hour
                        for price in costs[next_not_ok:status.index(1)+1]:
                            if price < costs[hour]:
                                next_lower_price = price
                                hour_next_lower_price = costs.index(price)
                                break
                        print(f"The first cheaper hour that we could have used is {hour_next_lower_price}:00.")
                        print(f"The price now: {costs[hour]}, and then: {next_lower_price}.")
                        print(f"Currently the power is {control_backup[hour]}, looking into range: ({int(control_min[hour])}, {int(control_max[hour]*10)})")

                        # Initialize 
                        storage = get_storage(control, parameters)   
                        lowest_storage_level = storage[hour_next_lower_price]
                        lowest_control = control[hour]
                                                
                        # Find the minimum power in that range that allows us to reach that cheaper hour
                        for c in range(int(control_min[hour]*10), int(control_max[hour]*10)+1):
                            
                            # Bring back the decimal
                            c /= 10
                            
                            # Define the new control sequence to test
                            test_control = control_backup.copy()
                            test_control[hour] = c

                            # Get the resulting status and storage sequence
                            test_status = get_status(test_control, parameters)
                            test_storage = get_storage(test_control, parameters)

                            # A lower control is valid only if the hour before the lower price hour is OK
                            if test_status[hour_next_lower_price-1]==0 and test_storage[hour_next_lower_price] < lowest_storage_level:
                                lowest_storage_level = test_storage[hour_next_lower_price]
                                lowest_control = c
                        
                        # Implement the solution
                        print(f"[DONE] A valid lower control level was: {lowest_control}")
                        control[hour] = lowest_control
                    
                    else:
                        print("\n[Constraint] No cheaper hour was reached\n[DONE]")

            # ----------------------------
            # Low noise hours
            # ----------------------------

            if key == "low_noise":
                print("\n[Constraint] Check if the hour is in the low noise hours.")
                if hour in parameters['constraints']['low_noise_hours']:
                    print("[DONE] The selected hour is in low noise hours. Run at maximum authorized.")
                    control_max[hour] == 0

    return control[hour], control_max[hour]

'''
Computes the status vector based on the current controls
'''
def get_status(control, parameters):

    # Extract from parameters
    N = parameters['horizon']
    load = parameters['loads']

    # When every hour must be satisfied
    if parameters['timestep'] == 'hourly':

        storage = [parameters['constraints']['initial_soc']] + [0 for i in range(N)]
        status = [1]*N
    
        # If the control and storage can supply the load, then the status is OK
        for hour in range(N):
            if storage[hour] + control[hour] >= load[hour]:
                storage[hour+1] = storage[hour] + control[hour] - load[hour]
                status[hour] = 0

    # When a full day must be satisfied
    elif parameters['timestep'] == 'daily':
        
        # Status is OK when daily load is satisfied
        if sum(control) >= parameters['required_control']:
            status = [0]*N
        else:
            status = [0]*(N-1) + [1]

    return status

def get_storage(control, parameters):
    """
    Computes the current storage levels for a given control sequence
    """

    storage = [parameters['constraints']['initial_soc']] + [0]*parameters['horizon']
    load = parameters['loads']

    for hour in range(parameters['horizon']):
        if storage[hour] + control[hour] >= load[hour]:
            storage[hour+1] = storage[hour] + control[hour] - load[hour]
    
    return storage


def iteration_plot(control, parameters):
    """
    Plots the current iteration
    """

    # Extract
    N = parameters['horizon']
    max_storage = parameters['constraints']['max_storage']
    control_max = parameters['control_max']
    control_min = [x*parameters['control_min_max_ratio'] for x in control_max]

    # Duplicate the last element of the hourly data for the plot
    costs_plot = parameters['elec_costs'] + [parameters['elec_costs'][-1]]
    controls_plot = control + [control[-1]]
    controls_max_plot = control_max + [control_max[-1]]
    controls_min_plot = control_min + [control_min[-1]]

    loads_plot = parameters['loads'] + [parameters['loads'][-1]]

    fig, ax = plt.subplots(1,1, figsize=(13,4))
    ax2 = ax.twinx()

    ax.step(range(N+1), loads_plot, where='post', color='red', alpha=0.4, label='Load')
    ax.step(range(N+1), controls_plot, where='post', color='blue', alpha=0.5, label='Control')
    ax.plot(range(N+1), get_storage(control, parameters), alpha=0.5, color='orange', label='Storage')
    ax.plot(range(N+1), [max_storage]*(N+1), alpha=0.2, linestyle='dotted', color='orange')
    #ax.plot(range(N+1), controls_max_plot, alpha=0.2, linestyle='dotted', color='blue')
    #ax.plot(range(N+1), controls_min_plot, alpha=0.2, linestyle='dotted', color='blue')
    ax2.step(range(N+1), costs_plot, where='post', color='gray', alpha=0.6, label='Cost')

    ax.set_xlabel("Time [hours]")
    ax.set_ylabel("Control variable")
    ax2.set_ylabel("Price per unit")

    ax.set_xticks(range(N+1))
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2)

    plt.show()


def compute_costs(control, parameters):
    """
    Computes the costs of the running the system with the current control strategy
    """

    costs = parameters['elec_costs']
    total_cost = 0

    for hour in range(parameters['horizon']):
        total_cost += costs[hour] * control[hour]

    print(f"The total cost of running the system during {parameters['horizon']} hours is {round(total_cost/1000,2)}")
