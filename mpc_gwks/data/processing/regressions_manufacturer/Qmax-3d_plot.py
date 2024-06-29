import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# The Q_max table
Q_max_table = [[0,-25,-20,-15,-7,-4,-2,2,7,10,15,18,20,35],
      [30,9250,10630,12000,14000,14000,14000,14000,14000,14000,14000,14000,14000,14000],
      [35,9000,10500,12000,14000,14000,14000,14000,14000,14000,14000,14000,14000,14000],
      [45,8500,10250,12000,14000,14000,14000,14000,14000,14000,14000,14000,14000,14000],
      [40,8750,10380,12000,14000,14000,14000,14000,14000,14000,14000,14000,14000,14000],
      [50,np.nan,10130,12000,14000,14000,14000,14000,14000,14000,14000,14000,14000,14000],
      [55,np.nan,11500,12000,14000,14000,14000,14000,14000,14000,14000,14000,14000,14000],
      [60,np.nan,np.nan,np.nan,14000,14000,14000,14000,14000,14000,14000,14000,14000,14000],
      [65,np.nan,np.nan,np.nan,np.nan,14000,14000,14000,14000,14000,14000,14000,14000,14000]]

Q_max = pd.DataFrame(Q_max_table[1:], columns=Q_max_table[0]).T
Q_max.columns = Q_max.iloc[0]
Q_max = Q_max[1:] / 1000  # Convert W to kW

# The approximated Q_max
def qmax(T_OA, T_sup_HP):
    if T_OA <= -15:
        return(-68851.589041 + (T_OA+273) * 313.315068)
    else:
        return 14000
        
# Define the range of values for T_OA and T_sup_HP
T_OA_range = np.linspace(-25, 20, 13)
T_sup_HP_range = np.linspace(30, 65, 8)

# Generate a grid of T_OA and T_sup_HP values
T_OA_grid, T_sup_HP_grid = np.meshgrid(T_OA_range, T_sup_HP_range)

# Calculate the Q_max for each combination of T_OA and T_sup_HP
Q_max_values = np.vectorize(qmax)(T_OA_grid, T_sup_HP_grid) / 1000

# Create a 3D plot
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(projection='3d')

# Plot the surface
surface = ax.plot_surface(T_OA_grid, T_sup_HP_grid, Q_max_values, cmap='viridis', alpha=0.7)

# Plot the exact values
for LWT in Q_max.columns.to_list():
    if LWT==30: ax.scatter(T_OA_range, [LWT for _ in range(13)], list(Q_max[LWT]), color='red', label="Manufacturer data")
    else: ax.scatter(T_OA_range, [LWT for _ in range(13)], list(Q_max[LWT]), color='red')

# Add labels and title
ax.set_xlabel('Outside air temperature (°C)')
ax.set_ylabel('Heat pump supply temperature (°C)')
ax.set_zlabel('Maximum heating power (kW)')

ax.set_xticks(T_OA_range)
ax.set_yticks(T_sup_HP_range)

# Modify xtick labels to display in Celsius
ax.set_xticklabels([f'{round(x)}' for x in T_OA_range])
# Modify ytick labels to display in Celsius
ax.set_yticklabels([f'{round(y)}' for y in T_sup_HP_range])

# Show the plot
plt.legend()
plt.show()
