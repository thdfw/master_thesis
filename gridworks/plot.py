import matplotlib.pyplot as plt
import numpy as np
import forecasts

def plot_MPC(data):

    fig, ax = plt.subplots(2,1, figsize=(8,5), sharex=True)
    
    # ------------------------------------------------------
    # First plot
    # ------------------------------------------------------
    
    ax[0].set_xlim([0,data['iterations']])

    # First plot part 1
    ax[0].plot(data['Q_load'], label="Load", color='red', alpha=0.4)
    ax[0].plot(data['Q_HP'],   label="HP", color='blue', alpha=0.4)
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
    ax[1].plot((data['iterations']+1)*[273+38], color='black', label="$T_{sup,load,min}$", alpha=0.4, linestyle='dashed')
    ax[1].set_ylabel("Temperatuere [K]")
    ax[1].set_xlabel("$Time [hours]$")
    ax[1].legend()

    plt.show()
