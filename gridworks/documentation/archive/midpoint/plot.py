import matplotlib.pyplot as plt
import numpy as np
import forecasts, optimizer, functions

'''
Prints the selected problem type
'''
def print_pb_type(pb_type):

    # Linearized or not
    if pb_type['linearized']: print("\nProblem type: Linearized")
    else: print("\nProblem type: Non-linear")

    # Variables: mixed integer or continuous
    if pb_type['mixed-integer']: print("Variables: Mixed-Integer")
    else: print("Variables: Continuous (relaxed or fixed binary)")

    # Solver: gurobi or ipopt/bonmin
    if pb_type['gurobi']: print("Solver: Gurobi")
    else: print("Solver: Bonmin") if pb_type['mixed-integer'] else print("Solver: Ipopt")
    
    print(f"\nTime step: {pb_type['delta_t_m']} minutes, with {pb_type['eta']} intermediate points")
    print(f"Horizon: {pb_type['horizon']*pb_type['delta_t_m']/60} hours ({pb_type['horizon']} time steps)")


'''
Prints the current iteration (x0, u0*, x1) in a way that is easy to visualize
'''
def print_iteration(u_opt, x_opt, x_1, pb_type):

    # ------------------------------------------------------
    # Initial state
    # ------------------------------------------------------
    u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
    x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]

    print("************************************************************************************")
    print("Initial state")
    print(f"B     -- {round(x_opt[0,0],1)} | S        {round(x_opt[12,0],1)} --    {round(x_opt[8,0],1)} --   {round(x_opt[4,0],0)} --")
    print(f"         {round(x_opt[1,0],1)} |          {round(x_opt[13,0],1)}       {round(x_opt[9,0],1)}      {round(x_opt[5,0],0)}")
    print(f"         {round(x_opt[2,0],1)} |          {round(x_opt[14,0],1)}       {round(x_opt[10,0],1)}      {round(x_opt[6,0],0)}")
    print(f"      -- {round(x_opt[3,0],1)} |       -- {round(x_opt[15,0],1)}    -- {round(x_opt[11,0],1)}   -- {round(x_opt[7,0],0)}")

    # ------------------------------------------------------
    # Mass flow rates
    # ------------------------------------------------------
    
    # Mass flow rates do not change with state => same for all intermediate states
    m_HP = round(functions.get_function("m_HP", u_opt_0, x_opt_0, 0, True, False),2) if u_opt_0[4]==1 else 0
    m_stor = round(u_opt[1,0],1)
    m_buffer = round(functions.get_function("m_buffer", u_opt_0, x_opt_0, 0, True, False),1)
    m_load = 0.2
    
    # Direction of flows
    S_t = f"-{m_stor}->" if round(u_opt_0[2])==0 else f"<-{m_stor}-"
    S_t2 = f"->" if round(u_opt_0[2])==0 else f"<-"
    B_t = f"-{m_buffer}->" if round(u_opt_0[3])==1 else f"<-{m_buffer}-"
    B_b = f"<-{m_buffer}-" if round(u_opt_0[3])==1 else f"-{m_buffer}->"
    
    # ------------------------------------------------------
    # Intermediate states up to final state
    # ------------------------------------------------------
    
    # Start at initial state
    x_inter = x_opt_0

    # From first all intermediate points until the final one
    for _ in range(pb_type['eta']+1):
    
        Q_HP = optimizer.get_function("Q_HP", u_opt_0, x_inter, 0, True, False)
        T_ret_HP = functions.get_function("T_ret_HP", u_opt_0, x_inter, 0, True, False)
        T_sup_load = functions.get_function("T_sup_load", u_opt_0, x_inter, 0, True, False)
        
        # Go to next intermediate point
        x_inter = optimizer.dynamics(u_opt_0, x_inter, 0, True, False, pb_type['eta'], pb_type['delta_t_m']*60)

        print("************************************************************************************")
        if _<pb_type['eta']: print(f"Intermediate state {_+1}")
        else: print(f"Final state")
        print(f"B {B_t} {round(x_inter[0],1)} | S        {round(x_inter[12],1)} {S_t2}    {round(x_inter[8],1)} {S_t2}   {round(x_inter[4],0)} {S_t}")
        print(f"         {round(x_inter[1],1)} |          {round(x_inter[13],1)}       {round(x_inter[9],1)}      {round(x_inter[5],0)}")
        print(f"         {round(x_inter[2],1)} |          {round(x_inter[14],1)}       {round(x_inter[10],1)}      {round(x_inter[6],0)}")
        print(f"  {B_b} {round(x_inter[3],1)} |   {S_t} {round(x_inter[15],1)}    {S_t2} {round(x_inter[11],1)}   {S_t2} {round(x_inter[7],0)}")
        
        print(f"\n{round(T_ret_HP,1) if round(u_opt[4,0])==1 else '-'} -{round(m_HP,2) if u_opt_0[4]==1 else 0}-> HP -{round(m_HP,2) if u_opt_0[4]==1 else 0}-> {round(u_opt[0,0],1) if round(u_opt[4,0])==1 else '-'} ({round(Q_HP,2) if round(u_opt[4,0])==1 else '-'} W)")

        print(f"{round(T_sup_load,1)} -{round(m_load,2)}-> Load -{round(m_load,2)}-> {round(T_sup_load-11.111,1)}")
        if _==pb_type['eta']: print("************************************************************************************")
        
    # ------------------------------------------------------
    # For the entire time step
    # ------------------------------------------------------
    
    Q_HP_average = optimizer.get_Q_HP_t(u_opt_0, x_opt_0, 0, True, False, pb_type['eta'], pb_type['delta_t_m']*60)
    print(f"\nQ_HP_average = {round(Q_HP_average,2)}")
    

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
    N = data['pb_type']['horizon']
    
    fig.suptitle(f"{linearized}, {variables}, {solver}, N={N} \nPrice: {data['elec_cost']} $, Elec: {data['elec_used']} kWh")
    
    # ------------------------------------------------------
    # First plot
    # ------------------------------------------------------
    
    # Get the Q_load from the m_load
    cp, Delta_T_load=  4187, 5/9*20
    Q_load_list = [m_load*cp*Delta_T_load for m_load in data['m_load']]
        
    ax[0].set_xlim([0,data['iterations']])

    # First plot part 1
    ax[0].plot(Q_load_list, label="Load", color='red', alpha=0.4)
    ax[0].plot(data['Q_HP'],   label="HP", color='blue', alpha=0.4)
    ax[0].set_ylim([0,20000])
    ax[0].set_ylabel("Power [W]")

    # First plot part 2
    ax2 = ax[0].twinx()
    ax2.plot(data['c_el'],     label="Price", color='black', alpha=0.4)
    ax2.set_ylabel("Price [$/MWh]")

    # x_ticks in hours
    tick_positions = np.arange(0, data['iterations']+1, step=int(60/data['pb_type']['delta_t_m']))
    tick_labels = [f"{step * data['pb_type']['delta_t_m'] // 60:02d}:00" for step in tick_positions]
    plt.xticks(tick_positions, tick_labels)

    # Common legend
    lines1, labels1 = ax[0].get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax[0].legend(lines1 + lines2, labels1 + labels2)
    
    # ------------------------------------------------------
    # Second plot
    # ------------------------------------------------------

    ax[1].plot(data['T_S11'], color='green', label="$T_{S11}$", alpha=0.4)
    ax[1].plot(data['T_S21'], color='orange', label="$T_{S21}$", alpha=0.4)
    ax[1].plot(data['T_S31'], color='red', label="$T_{S31}$", alpha=0.4)
    ax[1].plot(data['T_B4'], color='blue', label="$T_{B4}$", alpha=0.4)
    ax[1].plot((data['iterations']+1)*[273+38], color='black', label="$T_{sup,load,min}$", alpha=0.4, linestyle='dashed')
    ax[1].set_ylabel("Temperatuere [K]")
    ax[1].set_xlabel("$Time [hours]$")
    ax[1].legend()

    #plt.savefig('~/gridworks_ML/my_plot.png')
    plt.show()
