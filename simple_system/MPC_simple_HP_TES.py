'''
Title:
    MPC of a simple HP+TES system
    
Description:
    A "warm-up" problem on which to implement MPC before moving to more
    complex systems (e.g. GridWorks). Refer to the README for a detailed
    description of the system and model.
    
Author and date:
    Thomas Defauw
    Berkeley Lab, EPFL
    October 2023
'''

import casadi
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------
# MPC setup
# ------------------------------------------------------

# Time step
delta_t_m = 5            # min
delta_t_s = delta_t_m*60 # sec
delta_t_h = delta_t_m/60 # hours

# Horizon (10 hours)
N = int(10/delta_t_h)

# Simulation time (18 hours)
num_iterations = int(18/delta_t_h)

# Choice of solver (gurobi or ipopt)
GUROBI = True

print(f"\nMPC setup: \n\
- Time step: {delta_t_m} min \n\
- Horizon: {int(N*delta_t_h)} hours \n\
- Simulation: {int(num_iterations*delta_t_h)} hours \n\
- Solver: {'Gurobi' if GUROBI else 'ipopt'}")

# ------------------------------------------------------
# Constants and parameters
# ------------------------------------------------------

# Physical
cp = 4187 #J/kgK
rho = 997 #kg/m3

# Heat pump
m_HP = 0.5 #kg/s
T_HP_min = 273+30 #K
T_HP_max = 273+65 #K
Q_HP_min = 0 #W
Q_HP_max = 25000 #W
COP = 4

# Tank
tank_volume = 1 #m3
m_layer = rho * tank_volume/4 #kg
T_S_min = 273+10 #K
T_S_max = 273+90 #K

# Load
T_sup_min = 311 #K
Delta_T_load = 20 #K

# Punishment term for T_S1 < T_sup_min
c = 10**(2)

# Initial state of the tank
x_current = [273+20]*4

# Initialize for the final plot
elec, price = 0, 0
T_S1_list, T_S2_list, T_S3_list, T_S4_list = [0], [0], [0], [0]
T_S1_list[0], T_S2_list[0], T_S3_list[0], T_S4_list[0] = x_current
Q_HP_list = []

# ------------------------------------------------------
# Solver, variables and parameters
# ------------------------------------------------------

# Initialize casasdi
opti = casadi.Opti('conic') if GUROBI else casadi.Opti('nlp')

# Variables
x = opti.variable(4, N+1)   # States: T_S1,...,T_S4
u = opti.variable(1, N)     # Input:  T_HP
s = opti.variable(1, N+1)   # Slack variable for T_S1 < T_sup_min

# Parameters
c_el = opti.parameter(N)    # Electricity prices
Q_load = opti.parameter(N)  # Loads
x_0 = opti.parameter(4)     # Initial state

# Call solver with associated options
solver = 'gurobi' if GUROBI else 'ipopt'
solver_opts = {'gurobi.OutputFlag':0} if GUROBI else {'ipopt.print_level': 0, 'print_time': 0, 'ipopt.tol': 1e-4}
opti.solver(solver, solver_opts)

# ------------------------------------------------------
# Forecasts
# ------------------------------------------------------

# Hourly electricity prices in cts/kWh
c_el_all = [18.97, 18.92, 18.21, 16.58, 16.27, 15.49, 14.64, 18.93, 45.56,
26.42, 18.0, 17.17, 16.19, 30.74, 31.17, 16.18, 17.11, 20.24, 24.94, 24.69, 26.48, 30.15, 23.14, 24.11]

# Extend to match time step (1 hour is 1/delta_t_h time steps)
c_el_all = [item for item in c_el_all for _ in range(int(1/delta_t_h))]
    
# Convert to $/Wh and duplicate to 3 days
c_el_all = [x/100/1000 for x in c_el_all] * 3

# Heating loads in W
Q_load_all = ([2000]*12 + [5000]*10 + [10000]*30 + [15000]*30) * 30

# ------------------------------------------------------
# System dynamics
# ------------------------------------------------------

def dynamics(x_t, u_t, Q_load_t):
    
    # Constant temperature drop across the load
    m_load = Q_load_t / (cp * Delta_T_load)
    T_ret_load = x_t[0] - Delta_T_load
    
    # Change in energy stored = Rate of energy in - Rate of energy out
    x_t1_0 = x_t[0] + delta_t_s/(m_layer*cp) * (m_HP*cp*(u_t-x_t[0])    + m_load*cp*(x_t[1]-x_t[0]))
    x_t1_1 = x_t[1] + delta_t_s/(m_layer*cp) * (m_HP*cp*(x_t[0]-x_t[1]) + m_load*cp*(x_t[2]-x_t[1]))
    x_t1_2 = x_t[2] + delta_t_s/(m_layer*cp) * (m_HP*cp*(x_t[1]-x_t[2]) + m_load*cp*(x_t[3]-x_t[2]))
    x_t1_3 = x_t[3] + delta_t_s/(m_layer*cp) * (m_HP*cp*(x_t[2]-x_t[3]) + m_load*cp*(T_ret_load-x_t[3]))

    # Construct x(t+1)
    x_t1 = casadi.vertcat(x_t1_0, x_t1_1, x_t1_2, x_t1_3)
    
    return x_t1
    
# ------------------------------------------------------
# Constraints
# ------------------------------------------------------

# Initial state
opti.subject_to(x[:,0] == x_0)

for t in range(N):

    # Next state
    opti.subject_to(x[:,t+1] == dynamics(x[:,t], u[t], Q_load[t]))
    
    # Bounds on Q_HP
    opti.subject_to(m_HP*cp*(u[t]-x[3,t]) >= Q_HP_min)
    opti.subject_to(m_HP*cp*(u[t]-x[3,t]) <= Q_HP_max)
    
    # Bounds on T_HP
    opti.subject_to(u[t] >= T_HP_min)
    opti.subject_to(u[t] <= T_HP_max)

for t in range(N+1):

    # Bounds on storage tank temperature
    for i in range(4):
        opti.subject_to(x[i,t] >= T_S_min)
        opti.subject_to(x[i,t] <= T_S_max)
    
    # Soft constraint on minimum load supply temperature
    opti.subject_to(x[0,t] >= T_sup_min - s[t])
    opti.subject_to(s[t] >= 0)

# ------------------------------------------------------
# Objective function
# ------------------------------------------------------

# Sum of costs and punishment term (soft constraint) over the horizon
obj = sum(c_el[t] * delta_t_h * m_HP*cp*(u[t]-x[3,t])/COP + c*Q_load[t]*s[t] for t in range(N))
opti.minimize(obj)

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

for t in range(num_iterations):

    # Set x_0 to the current state
    opti.set_value(x_0, x_current)
    
    # Set forecasts for the next N steps
    opti.set_value(c_el, c_el_all[t:t+N])
    opti.set_value(Q_load, Q_load_all[t:t+N])

    # Solve opitmization problem and extract values
    sol = opti.solve()
    u_optimal = sol.value(u)
    x_optimal = sol.value(x)

    # Get the next state (obtained by implementing u_0*)
    x_current = x_optimal[:,1]

    # Print iteration
    hours = int(t*delta_t_h)
    minutes = round((t*delta_t_h-int(t*delta_t_h))*60)
    print("\n-----------------------------------------------------")
    print(f"Iteration {t+1} ({hours}h{minutes}min)")
    print("-----------------------------------------------------\n")
    print(f"x_0 = {[round(x,1) for x in x_optimal[:,0]]}")
    print(f"u_0 = {round(u_optimal[0],1)}")
    print(f"x_1 = {[round(x,1) for x in x_optimal[:,1]]}")
    
    # Prepare for plot
    T_S1_list.append(x_optimal[0,0])
    T_S2_list.append(x_optimal[1,0])
    T_S3_list.append(x_optimal[2,0])
    T_S4_list.append(x_optimal[3,0])
    Q_HP_list.append(m_HP*cp*(u_optimal[0]-x_optimal[3,0]))
    
    # Electricity and cost calculation
    elec   += m_HP*cp*(u_optimal[0]-x_optimal[3,0])/COP * delta_t_h
    price  += m_HP*cp*(u_optimal[0]-x_optimal[3,0])/COP * delta_t_h * c_el_all[t]

# ------------------------------------------------------
# Plot
# ------------------------------------------------------

fig, ax = plt.subplots(2,1, figsize=(10,6), sharex=True)
fig.suptitle(f"Electricity: {round(elec/1000,1)} kWh, Cost: {round(price,1)} $ \nN={int(N*delta_t_h)} hours, $\Delta t$={delta_t_m} minutes")

# First plot: power
ax[0].plot(Q_load_all[0:num_iterations], label="Load", color='red', alpha=0.4)
ax[0].plot(Q_HP_list, color='blue', label = "HP", alpha=0.4)
ax[0].set_ylabel("Power [W]")
ax[0].set_xlim([0,num_iterations])

# First plot: price
ax2 = ax[0].twinx()
ax2.plot([x*100*1000 for x in c_el_all[0:num_iterations]], label="Price", color='black', alpha=0.4)
ax2.set_ylabel("Price [cts/kWh]")

# Second plot
ax[1].plot(T_S1_list, color='orange', label="Tank top temperature", alpha=0.9)
ax[1].plot(T_S2_list, color='orange', alpha=0.6, linestyle='dashed')
ax[1].plot(T_S3_list, color='orange', alpha=0.5, linestyle='dashed')
ax[1].plot(T_S4_list, color='orange', alpha=0.4, linestyle='dashed')
ax[1].plot((num_iterations+1)*[T_sup_min], color='black', label="Minimum supply temperature", alpha=0.4, linestyle='dotted')
ax[1].set_ylabel("Temperatuere [K]")
ax[1].set_xlabel("Time [hours]")

# Legends
lines1, labels1 = ax[0].get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax[0].legend(lines1 + lines2, labels1 + labels2)
ax[1].legend()

# Time axis labels in hours
tick_positions = np.arange(0, num_iterations+1, step=12)
tick_labels = [f'{step * 5 // 60:02d}:00' for step in tick_positions]
plt.xticks(tick_positions, tick_labels)

plt.show()
