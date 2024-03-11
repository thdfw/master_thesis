import casadi
import numpy as np
import matplotlib.pyplot as plt
import optimizer, functions, plot, forecasts

def one_step_combi(combi, x_0):

    # ------------------------------------------------------
    # Time discretization
    # ------------------------------------------------------

    # Number of intermediate points between two time steps
    eta = 14

    # Time step
    delta_t_m = 2*(eta+1)       # minutes
    delta_t_h = delta_t_m/60    # hours
    delta_t_s = delta_t_m*60    # seconds

    # ------------------------------------------------------
    # Select problem type and solver
    # ------------------------------------------------------

    # Horizon (2 hours)
    N = int(2 * 1/delta_t_h)

    # Simulation time (16 hours)
    num_iterations = 1 #int(16 * 1/delta_t_h)

    # Problem type
    pb_type = {
    'linearized':       False,
    'mixed-integer':    False,
    'gurobi':           False,
    'horizon':          N,
    'eta':              eta,
    'delta_t_m':        delta_t_m,
    }

    # Print corresponding setup
    #plot.print_pb_type(pb_type)

    # ------------------------------------------------------
    # Initial state of the system
    # ------------------------------------------------------

    # Initial point around which to linearize
    a = [330, 0.25] + [0.6]*4 + x_0

    # ------------------------------------------------------
    # Initialize variables for the final plot
    # ------------------------------------------------------

    list_Q_HP = []
    list_S11, list_S21, list_S31, list_B4 = [x_0[4]], [x_0[8]], [x_0[12]], [x_0[3]]
    elec_cost, elec_used = 0, 0

    # ------------------------------------------------------
    # MPC
    # ------------------------------------------------------

    for iter in range(num_iterations):
        
        # Get u* and x*
        u_opt, x_opt, obj_opt = optimizer.optimize_N_steps(x_0, a, iter, pb_type, combi)
        print(f"Cost at optimal: {round(obj_opt,2)}")
    
    return round(obj_opt,4)
        
    '''
        # Extract u0* and x0
        u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
        x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]

        # Implement u_0* and obtain x_1
        x_1 = optimizer.next_state(u_t=u_opt_0, x_t=x_0, a=a, real=True, approx=False, eta=eta, delta_t_s=delta_t_s, t=0, combi=combi)

        # Print iteration
        plot.print_iteration(u_opt, x_opt, x_1, pb_type, 0, combi)
        
        # Update x_0
        x_0 = x_1
        
        # Update "a", the point around which we linearize
        a = u_opt_0[:2] + [0.6]*4 + x_1
        
        # ------------------------------------------------------
        # Plots
        # ------------------------------------------------------

        # Update total electricity use and cost
        Q_HP = functions.get_function("Q_HP", u_opt_0, x_opt_0, 0, True, False, 0, combi)
        elec_used += Q_HP/4 * delta_t_h
        elec_cost += Q_HP/4 * delta_t_h * forecasts.get_c_el(iter,iter+1,delta_t_h)[0]
    
        # Append values for the plot
        list_Q_HP.append(Q_HP)
        list_S11.append(x_1[4])
        list_S21.append(x_1[8])
        list_S31.append(x_1[12])
        list_B4.append(x_1[3])

    # Regroup the data and send it to plot
    plot_data = {
        'pb_type':      pb_type,
        'iterations':   num_iterations,
        'c_el':         forecasts.get_c_el(0,num_iterations,delta_t_h),
        'm_load':       forecasts.get_m_load(0,num_iterations,delta_t_h),
        'Q_HP':         list_Q_HP,
        'T_S11':        list_S11,
        'T_S21':        list_S21,
        'T_S31':        list_S31,
        'T_B4':         list_B4,
        'elec_cost':    round(elec_cost,2),
        'elec_used':    round(elec_used/1000,2),
    }

    print("\nPlotting the data...")
    plot.plot_MPC(plot_data)
    '''

def find_optimal_combi():
    
    # Initial state
    x_0 = [300.0]*4 + [300.0]*12

    min_cost = 100000
    save_combi = {
    'timestep0': [1,1],
    'timestep1': [1,1],
    'timestep2': [1,1],
    'timestep3': [1,1],
    }
    count = 0

    for i in range(2):
        for j in range(2):
            for ii in range(2):
                for jj in range(2):
                    for iii in range(2):
                        for jjj in range(2):
                            for iiii in range(2):
                                for jjjj in range(2):
                                
                                    # Better: if the energy in storage and buffer < the energy forecast of the load
                                    if np.max(x_0) < 311 and iiii == 0: continue

                                    d_ch_0 = iiii
                                    d_bu_0 = jjjj
                                    
                                    d_ch_1 = iii
                                    d_bu_1 = jjj
                            
                                    d_ch_2 = ii
                                    d_bu_2 = jj
                                    
                                    d_ch_3 = i
                                    d_bu_3 = j
                                    
                                    combi = {
                                    'timestep0': [d_ch_0, d_bu_0],
                                    'timestep1': [d_ch_1, d_bu_1],
                                    'timestep2': [d_ch_2, d_bu_2],
                                    'timestep3': [d_ch_3, d_bu_3],
                                    }
                                    
                                    # Compute cost, compare to min
                                    cost = one_step_combi(combi, x_0)
                                    if cost < min_cost:
                                        min_cost = cost
                                        save_combi = combi
                                        
                                    # If the cost is 0
                                    if cost == 0.0:
                                        return combi, cost
                                        
                                    count += 1
                                    print(f"End of NLP {count}/256")
                                    
    return save_combi, min_cost
                            
    
winning_combi, winning_cost = find_optimal_combi()
print("\nThe optimal combination and cost is:")
print(winning_combi)
print(winning_cost)
