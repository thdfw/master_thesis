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
    
    print(f"\nTime step: {pb_type['time_step']} minutes")
    print(f"Horizon: {pb_type['horizon']*pb_type['time_step']/60} hours ({pb_type['horizon']} time steps)")


'''
Prints the current iteration (x0, u0*, x1) in way that is easy to visualize
'''
def print_iteration(u_opt, x_opt, x_1, pb_type):

    u_opt_0 = [round(float(x),6) for x in u_opt[:,0]]
    x_opt_0 = [round(float(x),6) for x in x_opt[:,0]]
    
    S_t = "->" if round(u_opt_0[2])==0 else "<-"
    S_b = "<-" if round(u_opt_0[2])==0 else "->"
    B_t = "->" if round(u_opt_0[3])==1 else "<-"
    B_b = "<-" if round(u_opt_0[3])==1 else "->"

    print(f"\nBuffer {B_t} {round(x_opt[0,0],1)} | Storage  {round(x_opt[12,0],1)} {S_t}    {round(x_opt[8,0],1)} {S_t}   {round(x_opt[4,0],0)} {S_t}")
    print(f"          {round(x_opt[1,0],1)} |          {round(x_opt[13,0],1)}       {round(x_opt[9,0],1)}      {round(x_opt[5,0],0)}")
    print(f"          {round(x_opt[2,0],1)} |          {round(x_opt[14,0],1)}       {round(x_opt[10,0],1)}      {round(x_opt[6,0],0)}")
    print(f"       {B_b} {round(x_opt[3,0],1)} |       {S_t} {round(x_opt[15,0],1)}    {S_t} {round(x_opt[11,0],1)}   {S_t} {round(x_opt[7,0],0)}\n")

    m_HP = functions.get_function("m_HP", u_opt_0, x_opt_0, 0, True, False)
    m_buffer = functions.get_function("m_buffer", u_opt_0, x_opt_0, 0, True, False)
    T_ret_HP = functions.get_function("T_ret_HP", u_opt_0, x_opt_0, 0, True, False)
    T_sup_load = functions.get_function("T_sup_load", u_opt_0, x_opt_0, 0, True, False)

    print(f"T_sup_HP = {round(u_opt[0,0],1) if round(u_opt[4,0])==1 else '-'}")
    print(f"T_ret_HP = {round(T_ret_HP,1) if round(u_opt[4,0])==1 else '-'}")
    print(f"Q_HP = {round(0.5 * 4187 * (u_opt[0,0] - T_ret_HP) * u_opt[4,0],1) if round(u_opt[4,0])==1 else '-'}")
    print(f"m_HP = {round(m_HP,2) if u_opt_0[4]==1 else 0}, m_stor = {round(u_opt[1,0],2)}, m_buffer = {round(m_buffer,2)}, m_load = 0.2")
    print(f"=> T_sup_load = {round(T_sup_load,1)}")

    print(f"\nBuffer {B_t} {round(x_1[0],1)} | Storage  {round(x_1[12],1)} {S_t}    {round(x_1[8],1)} {S_t}   {round(x_1[4],0)} {S_t}")
    print(f"          {round(x_1[1],1)} |          {round(x_1[13],1)}       {round(x_1[9],1)}      {round(x_1[5],0)}")
    print(f"          {round(x_1[2],1)} |          {round(x_1[14],1)}       {round(x_1[10],1)}      {round(x_1[6],0)}")
    print(f"       {B_b} {round(x_1[3],1)} |       {S_t} {round(x_1[15],1)}    {S_t} {round(x_1[11],1)}   {S_t} {round(x_1[7],0)}")


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
    tick_positions = np.arange(0, data['iterations']+1, step=12)
    tick_labels = [f'{step * 5 // 60:02d}:00' for step in tick_positions]
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

    plt.show()
