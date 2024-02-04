import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import load_forecast, pareto_algorithm

print("\n--------------------------------")
print("0 - Find the best forecaster")
print("--------------------------------")

# Get past data
past_data = load_forecast.get_past_data()

# Find the forecaster that performs best on past data
best_forecaster, model = load_forecast.get_best_forecaster(past_data)

print(f"\nThe forecaster that performed best on the past data is {best_forecaster}.")

print("\n--------------------------------")
print("1 - Import weather forecast")
print("--------------------------------")

# Temporary, need to replace with pvlib
df = pd.read_excel(os.getcwd()+'/data/gridworks_yearly_data.xlsx', header=3, index_col = 0)
df.index = pd.to_datetime(df.index)
df.index.name = None
df['Outside Temp F'] = df['Outside Temp F'].apply(lambda x: round(5/9 * (x-32),2))
weather = list(df['Outside Temp F'][24*60:24*61])

print(f"\n{len(weather)}-hour weather forecast succesfully obtained:\n{weather}")

print("\n--------------------------------")
print("2 - Get forecasted load")
print("--------------------------------")

# (1-delta)*100 confidence interval
delta = 0.05
pred_load, min_pred_load, max_pred_load = load_forecast.get_forecast_CI(weather, best_forecaster, model, delta)
print(f"\nFinished predicting the load with {best_forecaster}, {(1-delta)*100}% confidence interval.")
print([round(x[0],2) for x in pred_load])

print("\n--------------------------------")
print("3 - Get HP commands from Pareto")
print("--------------------------------")

# Select price forecast (options are: "GridWorks", "Progressive", "Peter")
price_forecast = "GridWorks"

# Select temperature of water going to the HPs (Celcius)
T_HP_in = 55

# Select maximum storage capacity (kWh)
max_storage = 30

# Get the operation over the forecsats
Q_HP, storage, total_cost, total_energy, c_el = pareto_algorithm.get_pareto(pred_load, price_forecast, weather, T_HP_in, max_storage, False)

print("\nObtained the solution from the pareto algorithm.")

# Duplicate the last element of the hourly data for the plot
N = len(c_el)
c_el2 = c_el + [c_el[-1]]
Q_HP = [round(x,3) for x in Q_HP + [Q_HP[-1]]]
load2 = pred_load + [pred_load[-1]]

# Plot the state of the system
fig, ax = plt.subplots(1,1, figsize=(13,4))
plt.title(f"Cost: {total_cost}$, Supplied: {total_energy} kWh_th \n=> {round(100*total_cost/total_energy,2)} cts/kWh_th")
ax2 = ax.twinx()
ax2.step(range(N+1), c_el2, where='post', color='gray', alpha=0.6, label='Cost per kWh_th')
ax.step(range(N+1), load2, where='post', color='red', alpha=0.4, label='Load')
ax.step(range(N+1), Q_HP, where='post', color='blue', alpha=0.5, label='HP')
ax.plot(storage, color='orange', alpha=0.6, label='Storage')
ax.plot(range(N+1), [max_storage]*(N+1), alpha=0.2, linestyle='dotted', color='gray')
ax.set_ylim([0,35])
ax.set_xticks(range(N+1))
ax.set_xlabel("Time [hours]")
ax.set_ylabel("Heat [kWh_th]")
ax2.set_ylabel("Price [cts/kWh_th]")
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2)
plt.show()
