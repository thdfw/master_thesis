import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import datetime as dtm
import math
import load_forecast, pareto_algorithm, weather_forecast

# Rendering
PLOT = False
PRINT = False

# Simulation start and length
day_of_the_year = 0
num_hours = 365*24
horizon = 24

# Get weather forecast
df = pd.read_excel(os.getcwd()+'/data/gridworks_yearly_data.xlsx', header=3, index_col = 0)
df.index = pd.to_datetime(df.index)
df.index.name = None
df['Outside Temp F'] = df['Outside Temp F'].apply(lambda x: round(5/9 * (x-32),2))
weather_total = list(df['Outside Temp F'][24*day_of_the_year:24*day_of_the_year+num_hours+horizon])
weather_total += list(df['Outside Temp F'][:24])
final_CI = [0]*horizon

# Get prices
df = pd.read_excel(os.getcwd()+'/data/gridworks_yearly_data.xlsx', header=3, index_col = 0)
df.index = pd.to_datetime(df.index)
df.index.name = None
df['c_el'] = df['Rt Energy Price ($/MWh)'] + df['Dist Price ($/MWh)']
c_el = list(df['c_el'][24*day_of_the_year:24*day_of_the_year+num_hours+horizon])
c_el += list(df['c_el'][:24])

# ---------------------------------------
# Parameters
# ---------------------------------------

# Temperature of water going to the HPs (Celcius)
T_HP_in = 57

# Minimum temperature of water going to the PCM (Celcius)
T_sup_HP_min = 58

# Maximum storage capacity (kWh)
max_storage = 14*2

# Select price forecast (options are: "GridWorks", "Progressive", "Peter")
price_forecast = "year"

# Initial state
SoC_0 = 0

# All lists for final plot
Q_HP_list = []
load_list = []
c_el_list = []
SOC_list = [SoC_0]

# ---------------------------------------
print("0 - Find the best forecaster")
# ---------------------------------------

# Get past data
path_to_past_data = os.getcwd()+'/data/gridworks_yearly_data.xlsx'
past_data = load_forecast.get_past_data(path_to_past_data)

# Find the forecaster that performs best on past data
best_forecaster, model = load_forecast.get_best_forecaster(past_data, path_to_past_data)

print(f"The forecaster that performed best on the past data is {best_forecaster}.")

print("\n---------------------------------------")
print("-- RUN PARETO MPC --")
print("---------------------------------------")

for iter in range(num_hours):
    
    print("\n---------------------------------------")
    print(f"Day {int(iter/24)}, hour {iter%24}:00")
    print("---------------------------------------")
    
    print(f"Current storage level: {SoC_0} kWh")

    # ---------------------------------------
    print("1 - Get weather forecast")
    # ---------------------------------------
    
    weather = weather_total[iter:iter+horizon]
    if PRINT: print([round(x,1) for x in weather])
    if PRINT: print(f"\n{horizon}-hour weather forecast succesfully obtained.")
    
    # ---------------------------------------
    print("2 - Get forecasted load")
    # ---------------------------------------

    delta = 0.05
    pred_load, _, __ = load_forecast.get_forecast_CI(weather, best_forecaster, model, delta, path_to_past_data)
    if PRINT: print(f"\nLoad succesfully predicted with {best_forecaster}.")
    
    # ---------------------------------------
    print("3 - Get HP commands from Pareto")
    # ---------------------------------------

    # Get the operation over the forecsats
    Q_HP, m_HP = pareto_algorithm.get_pareto(pred_load, price_forecast, weather, T_HP_in, T_sup_HP_min, max_storage, 
                                             False, False, horizon, final_CI, iter+24*day_of_the_year, SoC_0)

    if PRINT: print(f"Obtained the solution from the pareto algorithm.\nQ_HP = {Q_HP}")
        
    # ---------------------------------------
    print("4 - Simulate")
    # ---------------------------------------

    SoC_1 = SoC_0 + Q_HP[0] - pred_load[0]
    SoC_1 = SoC_1[0]
    
    # Prepare for next iteration: get the intial storage
    SoC_0 = SoC_1

    # Extend all lists for final plot
    Q_HP_list.append(Q_HP[0])
    load_list.append(pred_load[0][0])
    SOC_list.append(SoC_1)
      
# Compute the cost
total_opex = 0
for hour in range(len(Q_HP_list)):
    total_opex += Q_HP_list[hour] * c_el[hour] # you forgot the COP!
print(f"The total cost of running the system during {num_hours/24} days: {round(total_opex/1000,2)} $")
     
print("\n\nQ_HP:")
print(Q_HP_list[:num_hours])

print("\nc_el:")
print([round(x,2) for x in c_el[:num_hours]])
print("")

# Final plot
fig, ax = plt.subplots(1,1, figsize=(13,4))
ax.step(range(num_hours), load_list, where="post", color="red", alpha=0.5)
ax.step(range(num_hours), Q_HP_list, where="post", color="blue", alpha=0.5)
ax.plot(SOC_list, color="orange", alpha=0.5)
ax2 = ax.twinx()
ax2.step(range(num_hours), c_el[:num_hours], where="post", color="gray", alpha=0.5)

ax.set_xlabel("Time [hours]")
ax.set_ylabel("Energy [kWh]")
ax2.set_ylabel("Electricity price [cts/kWh]")

#ax.legend(loc='upper left')
#ax2.legend(loc='upper right')

plt.show()
