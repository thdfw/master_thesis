import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import forecasts, functions
from sequencer import current_datetime
from sequencer import BONMIN
delta_t_h = 4/60

'''
Prints the selected problem type
'''
def print_pb_type(pb_type, num_iterations):

    # Linearized or not
    if pb_type['linearized']: print("\nProblem type: Linearized")
    else: print("\nProblem type: Non-linear")

    # Variables: mixed integer or continuous
    if pb_type['mixed-integer']: print("Variables: Mixed-Integer")
    else: print("Variables: Continuous (fixed binary)")

    # Solver: gurobi or ipopt/bonmin
    if pb_type['gurobi']: print("Solver: Gurobi")
    else: print("Solver: Bonmin") if pb_type['mixed-integer'] else print("Solver: Ipopt")
    
    # Sequencer solver: gurobi or bonmin
    print("Sequencer Solver: Bonmin") if BONMIN else print("Sequencer Solver: Gurobi")
    
    # Time step and horizon
    print(f"\nTime step: {pb_type['time_step']} minutes \nIntegration method: {pb_type['integration']}")
    print(f"Horizon: {pb_type['horizon']*pb_type['time_step']/60} hours ({pb_type['horizon']} time steps)")
    print(f"Simulation: {num_iterations} hours ({num_iterations} iterations)")

'''
Prints the current iteration (x0, u0*, x1) in way that is easy to visualize
'''
def print_iteration(u_opt, x_opt, x_1, sequence, iter):

    # ------------------------------------------------------
    # Initial state
    # ------------------------------------------------------

    u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
    x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]
    
    print("\nInitial state")
    print(f"B     -- {round(x_opt[0,0],1)} | S        {round(x_opt[12,0],1)} --    {round(x_opt[8,0],1)} --   {round(x_opt[4,0],0)} --")
    print(f"         {round(x_opt[1,0],1)} |          {round(x_opt[13,0],1)}       {round(x_opt[9,0],1)}      {round(x_opt[5,0],0)}")
    print(f"         {round(x_opt[2,0],1)} |          {round(x_opt[14,0],1)}       {round(x_opt[10,0],1)}      {round(x_opt[6,0],0)}")
    print(f"      -- {round(x_opt[3,0],1)} |       -- {round(x_opt[15,0],1)}    -- {round(x_opt[11,0],1)}   -- {round(x_opt[7,0],0)}")
    
    # ------------------------------------------------------
    # Get hourly average mass flow rates, get heat values
    # ------------------------------------------------------
    
    Q_HP = []
    m_HP = []
    m_stor, m_buffer = 0, 0

    for k in range(15):
    
        u_k = [round(float(x),6) for x in u_opt[:,k]]
        x_k = [round(float(x),6) for x in x_opt[:,k]]
        
        Q_HP.append(functions.get_function("Q_HP", u_k, x_k, 0, sequence, iter))
        m_HP.append(round(functions.get_function("m_HP", u_k, x_k, 0, sequence, iter),2))
        m_buffer += round(functions.get_function("m_buffer", u_k, x_k, 0, sequence, iter),1)
        m_stor += u_opt[1,k]

    m_buffer = round(m_buffer/15, 1)
    m_stor = round(m_stor/15, 1)
    
    # Round -0.0 values to 0.0
    if m_buffer<=0 and m_buffer>-0.04: m_buffer = 0.0
    if m_stor<=0   and m_stor>-0.04:   m_stor = 0.0

    # ------------------------------------------------------
    # Next state
    # ------------------------------------------------------
    
    S_t = f"-{m_stor}->"    if round(u_opt_0[2])==0 else f"<-{m_stor}-"
    S_t2 = f"->"            if round(u_opt_0[2])==0 else f"<-"
    B_t = f"-{m_buffer}->"  if round(u_opt_0[3])==1 else f"<-{m_buffer}-"
    B_b = f"<-{m_buffer}-"  if round(u_opt_0[3])==1 else f"-{m_buffer}->"
    
    print("\nNext state")
    print(f"B {B_t} {round(x_1[0],1)} | S        {round(x_1[12],1)} {S_t2}    {round(x_1[8],1)} {S_t2}   {round(x_1[4],0)} {S_t}")
    print(f"         {round(x_1[1],1)} |          {round(x_1[13],1)}       {round(x_1[9],1)}      {round(x_1[5],0)}")
    print(f"         {round(x_1[2],1)} |          {round(x_1[14],1)}       {round(x_1[10],1)}      {round(x_1[6],0)}")
    print(f"  {B_b} {round(x_1[3],1)} |   {S_t} {round(x_1[15],1)}    {S_t2} {round(x_1[11],1)}   {S_t2} {round(x_1[7],0)}")
    
    m_HP = m_HP if u_opt_0[4]==1 else 0
    m_load = forecasts.get_m_load(iter, iter+1, delta_t_h)
    
    print(f"\nQ_HP = {[round(x/1000) for x in Q_HP]} kW")
    # print(f"m_HP = {m_HP} kg/s \nm_load = {m_load} kg/s")
    print(f"m_load = {m_load} kg/s")
    # print(f"Resistive elements: {[round(float(x),1) for x in u_opt[5,0:15]]}\n")
    
    '''
    print(f"\n\nNEXT HOUR INPUTS:")
    print(f"m_stor = {[round(x,4) for x in u_opt[1,:15]]}")
    print(f"m_load = {[m_load for _ in range(15)]}")
    print(f"T_sup_HP = {[round(x,2) for x in u_opt[0,:15]]}")
    print(f"delta_HP = {u_opt[4,:15]}")
    print("")
    '''

'''
The final plot with all the data accumulated during the simulation
'''
def plot_MPC(data, FMU, DETAILED):

    fig, ax = plt.subplots(2,1, figsize=(8,5), sharex=True)
    
    # ------------------------------------------------------
    # Plot title
    # ------------------------------------------------------
    
    linearized = "Linearized" if data['pb_type']['linearized'] else "Non linear"
    variables = "Mixed-Integer" if data['pb_type']['mixed-integer'] else "Continuous"
    solver = "Gurobi" if data['pb_type']['gurobi'] else "Ipopt"
    solver += " and Bonmin" if BONMIN else " and Gurobi"
    N = data['pb_type']['horizon']
    
    fig.suptitle(f"Horizon: {int(N/15)} hours, time step: 4 minutes \nCost: {data['elec_cost']} $, Electricity used: {data['elec_used']} kWh, Heat supplied: {data['heat_supp']} kWh")
    
    # Get the Q_load from the m_load
    cp, Delta_T_load= 4187, 5/9*20
    Q_load_list = [m_load*cp*Delta_T_load for m_load in data['m_load']]

    # ------------------------------------------------------
    # First plot
    # ------------------------------------------------------
    
    ax[0].set_xlim([0,15*data['iterations']])

    # HP and load
    from matplotlib.ticker import FuncFormatter
    ax[0].plot(data['Q_HP'], label="Heat pump", color='blue', alpha=0.4)
    ax[0].plot(Q_load_list, label="Load", color='red', alpha=0.4)
    ax[0].set_ylim([0,20000])
    ax[0].set_yticks(list(range(0,21000,4000)))
    ax[0].yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '{:.0f}'.format(x / 1000)))
    ax[0].set_ylabel("Power [kW]")

    # Electricity price
    ax2 = ax[0].twinx()
    ax2.plot([x*100*1000 for x in data['c_el']], label="Price", color='black', alpha=0.4)
    ax2.set_ylabel("Price [cts/kWh]")
    ax2.set_yticks(list(range(0, int(max(data['c_el'])*100*1000+10), 10)))
    
    # x_ticks in hours
    tick_positions = np.arange(0, data['iterations']*15+1, step=int(60/data['pb_type']['time_step']))
    tick_labels = [f"{step * data['pb_type']['time_step'] // 60}" for step in tick_positions]
    plt.xticks(tick_positions, tick_labels)

    # Common legend
    ax[0].legend(loc='upper left')
    ax2.legend(loc='upper right')

    # ------------------------------------------------------
    # State of charge computation
    # ------------------------------------------------------
    
    max_temp, min_temp = 65+273, 38+273
    avg_B_T, avg_S_T, SoC_B, SoC_S = [], [], [], []
    
    # Compute buffer SoC
    for k in range(len(data['T_B1'])):
        avg_B_T_k = (data['T_B1'][k] + data['T_B2'][k] + data['T_B3'][k] + data['T_B4'][k])/4
        avg_B_T.append(avg_B_T_k)
        SoC_B.append((avg_B_T_k-min_temp)/(max_temp-min_temp))
        
    # Compute storage SoC
    for k in range(len(data['T_S11'])):
        avg_S_T_k = 0
        avg_S_T_k += data['T_S11'][k] + data['T_S12'][k] + data['T_S13'][k] + data['T_S14'][k]
        avg_S_T_k += data['T_S21'][k] + data['T_S22'][k] + data['T_S23'][k] + data['T_S24'][k]
        avg_S_T_k += data['T_S31'][k] + data['T_S32'][k] + data['T_S33'][k] + data['T_S34'][k]
        avg_S_T_k = avg_S_T_k/12
        avg_S_T.append(avg_S_T_k)
        SoC_S.append((avg_S_T_k-min_temp)/(max_temp-min_temp))
        
    # ------------------------------------------------------
    # Second plot
    # ------------------------------------------------------

    # Show temperatures inside tanks
    if DETAILED:
    
        # Convert all temperatures to °C
        data['T_B1'] = [x-273 for x in data['T_B1']]
        data['T_B4'] = [x-273 for x in data['T_B4']]
        data['T_S11'] = [x-273 for x in data['T_S11']]
        data['T_S21'] = [x-273 for x in data['T_S21']]
        data['T_S31'] = [x-273 for x in data['T_S31']]
        if FMU:
            data['T_B1_pred'] = [x-273 for x in data['T_B1_pred']]
            data['T_B4_pred'] = [x-273 for x in data['T_B4_pred']]
            data['T_S11_pred'] = [x-273 for x in data['T_S11_pred']]
            data['T_S21_pred'] = [x-273 for x in data['T_S21_pred']]
            data['T_S31_pred'] = [x-273 for x in data['T_S31_pred']]
            
        ax[1].plot(data['T_S11'], color='green', label="$T_{S11}$", alpha=0.4)
        if FMU: ax[1].plot(data['T_S11_pred'], color='green', alpha=0.4, linestyle='dotted')
        ax[1].plot(data['T_S21'], color='orange', label="$T_{S21}$", alpha=0.4)
        if FMU: ax[1].plot(data['T_S21_pred'], color='orange', alpha=0.4, linestyle='dotted')
        ax[1].plot(data['T_S31'], color='red', label="$T_{S31}$", alpha=0.4)
        if FMU: ax[1].plot(data['T_S31_pred'], color='red', alpha=0.4, linestyle='dotted')
        ax[1].plot(data['T_B1'], color='blue', label="$T_{B1}$", alpha=0.4)
        if FMU: ax[1].plot(data['T_B1_pred'], color='blue', alpha=0.4, linestyle='dotted')
        ax[1].plot(data['T_B4'], color='purple', label="$T_{B4}$", alpha=0.4)
        if FMU: ax[1].plot(data['T_B4_pred'], color='purple', alpha=0.4, linestyle='dotted')
        ax[1].plot((data['iterations']*15+1)*[38], color='black', label="$T_{load,in}^{min}$", alpha=0.2, linestyle='dashed')
        ax[1].set_ylabel("Temperatuere [°C]")
        ax[1].set_xlabel("Time [hours]")
        ax[1].set_ylim([30,70])
        ax[1].set_yticks(list(range(30,80,10)))
        ax[1].legend(loc='upper right')
        
        # Convert all temperatures back to K
        data['T_B1'] = [x+273 for x in data['T_B1']]
        data['T_B4'] = [x+273 for x in data['T_B4']]
        data['T_S11'] = [x+273 for x in data['T_S11']]
        data['T_S21'] = [x+273 for x in data['T_S21']]
        data['T_S31'] = [x+273 for x in data['T_S31']]
        if FMU:
            data['T_B1_pred'] = [x+273 for x in data['T_B1_pred']]
            data['T_B4_pred'] = [x+273 for x in data['T_B4_pred']]
            data['T_S11_pred'] = [x+273 for x in data['T_S11_pred']]
            data['T_S21_pred'] = [x+273 for x in data['T_S21_pred']]
            data['T_S31_pred'] = [x+273 for x in data['T_S31_pred']]
        
    # Show state of charge only
    else:
        ax[1].plot(SoC_B, color='orange', label='Buffer', linestyle='dashed')
        ax[1].plot(SoC_S, color='orange', label='Storage')
        ax[1].set_ylim([0,1])
        ax[1].yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '{:.0f}'.format(x * 100)))
        ax[1].set_ylabel("State of charge [%]")
        ax[1].set_xlabel("Time [hours]")
        ax[1].legend(loc='upper right')

    # Save the plot as a png
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    plt.savefig(os.path.join("data", "simulations", "recent", "plot_" + formatted_datetime + ".png"))
    plt.show()

'''
To visualize the 8 hours predicted by a single iteration
'''
def plot_single_iter(data):

    fig, ax = plt.subplots(2,1, figsize=(8,5), sharex=True)
    fig.suptitle(f"Sequence: {data['sequence']}")

    # ------------------------------------------------------
    # First plot
    # ------------------------------------------------------
    
    # Get the Q_load from the m_load
    cp, Delta_T_load=  4187, 5/9*20
    Q_load_list = [m_load*cp*Delta_T_load for m_load in data['m_load']]
    
    # HP and load
    ax[0].plot(Q_load_list, label="Load", color='red', alpha=0.4)
    ax[0].plot(data['Q_HP'], label="HP", color='blue', alpha=0.4)
    ax[0].set_xlim([0,120])
    ax[0].set_ylim([0,20000])
    ax[0].set_ylabel("Power [W]")

    # Electricity price
    ax2 = ax[0].twinx()
    ax2.plot(data['c_el'], label="Price", color='black', alpha=0.4)
    ax2.set_ylabel("Price [cts/kWh]")
    ax2.set_ylim([0,50])
    
    # Common legend
    lines1, labels1 = ax[0].get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax[0].legend(lines1 + lines2, labels1 + labels2)
    
    # ------------------------------------------------------
    # Second plot
    # ------------------------------------------------------
    
    # Temperatures in storage and buffer
    ax[1].plot(data['T_S11'], color='green', label="$T_{S11}$", alpha=0.4)
    ax[1].plot(data['T_S21'], color='orange', label="$T_{S21}$", alpha=0.4)
    ax[1].plot(data['T_S31'], color='red', label="$T_{S31}$", alpha=0.4)
    ax[1].plot(data['T_B1'], color='blue', label="$T_{B1}$", alpha=0.4)
    ax[1].plot(data['T_B4'], color='blue', label="$T_{B4}$", alpha=0.4, linestyle='dashed')
    ax[1].plot((120)*[273+38], color='black', label="$T_{load,in}^{min}$", alpha=0.2, linestyle='dotted')
    ax[1].set_ylabel("Temperatuere [K]")
    ax[1].set_xlabel("Time steps")
    ax[1].legend()

    plt.show()
