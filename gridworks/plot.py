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
    print(f"\nTime step: {pb_type['time_step']} minutes")
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
    m_stor, m_buffer = 0, 0

    for k in range(15):
    
        u_k = [round(float(x),6) for x in u_opt[:,k]]
        x_k = [round(float(x),6) for x in x_opt[:,k]]
        
        Q_HP.append(functions.get_function("Q_HP", u_k, x_k, 0, sequence, iter))
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
    
    m_HP = 0.5 if u_opt_0[4]==1 else 0
    m_load = forecasts.get_m_load(iter, iter+1, delta_t_h)
    
    print(f"\nQ_HP = {[round(x/1000) for x in Q_HP]} kW")
    print(f"m_HP = {m_HP} kg/s, m_load = {m_load} kg/s")
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
def plot_MPC(data):

    fig, ax = plt.subplots(2,1, figsize=(8,5), sharex=True)
    
    # ------------------------------------------------------
    # Plot title
    # ------------------------------------------------------
    
    linearized = "Linearized" if data['pb_type']['linearized'] else "Non linear"
    variables = "Mixed-Integer" if data['pb_type']['mixed-integer'] else "Continuous"
    solver = "Gurobi" if data['pb_type']['gurobi'] else "Ipopt"
    solver += " and Bonmin" if BONMIN else " and Gurobi"
    N = data['pb_type']['horizon']
    
    # Get the Q_load from the m_load
    cp, Delta_T_load= 4187, 5/9*20
    Q_load_list = [m_load*cp*Delta_T_load for m_load in data['m_load']]
    
    fig.suptitle(f"{linearized}, {variables}, {solver}, N={N} \nPrice: {data['elec_cost']} $, Elec: {data['elec_used']} kWh_e, Supplied: {round(sum(data['Q_HP'])/1000/15,1)} kWh_th")
    
    # ------------------------------------------------------
    # First plot
    # ------------------------------------------------------
    
    ax[0].set_xlim([0,15*data['iterations']])

    # HP and load
    ax[0].plot(data['Q_HP'], label="Heat pump", color='blue', alpha=0.4)
    ax[0].plot(Q_load_list, label="Load", color='red', alpha=0.4)
    ax[0].set_ylim([0,20000])
    ax[0].set_ylabel("Power [W]")

    # Electricity price
    ax2 = ax[0].twinx()
    ax2.plot([x*100*1000 for x in data['c_el']], label="Price", color='black', alpha=0.4)
    ax2.set_ylabel("Price [cts/kWh]")
    #ax2.set_ylim([-20,50])

    # x_ticks in hours
    tick_positions = np.arange(0, data['iterations']*15+1, step=int(60/data['pb_type']['time_step']))
    tick_labels = [f"{step * data['pb_type']['time_step'] // 60:02d}:00" for step in tick_positions]
    plt.xticks(tick_positions, tick_labels)

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
    ax[1].plot((data['iterations']*15+1)*[273+38], color='black', label="$T_{sup,load,min}$", alpha=0.2, linestyle='dotted')
    ax[1].set_ylabel("Temperatuere [K]")
    ax[1].set_xlabel("Time [hours]")
    ax[1].legend()

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
    ax[1].plot((120)*[273+38], color='black', label="$T_{sup,load,min}$", alpha=0.2, linestyle='dotted')
    ax[1].set_ylabel("Temperatuere [K]")
    ax[1].set_xlabel("Time steps")
    ax[1].legend()

    plt.show()
