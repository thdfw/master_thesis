import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import load_forecast, pareto_algorithm, fmu_simulation

print("\n---------------------------------------")
print("0 - Find the best forecaster")
print("---------------------------------------")

# Get past data
path_to_past_data = os.getcwd()+'/data/gridworks_yearly_data.xlsx'
past_data = load_forecast.get_past_data(path_to_past_data)

# Find the forecaster that performs best on past data
best_forecaster, model = load_forecast.get_best_forecaster(past_data, path_to_past_data)

print(f"\nThe forecaster that performed best on the past data is {best_forecaster}.")

print("\n---------------------------------------")
print("1 - Import weather forecast")
print("---------------------------------------")

# Lenght of simulation (days)
num_days = 1

# Temporary, need to replace with pvlib
df = pd.read_excel(os.getcwd()+'/data/gridworks_yearly_data.xlsx', header=3, index_col = 0)
df.index = pd.to_datetime(df.index)
df.index.name = None
df['Outside Temp F'] = df['Outside Temp F'].apply(lambda x: round(5/9 * (x-32),2))
day_of_the_year = 60
weather = list(df['Outside Temp F'][24*day_of_the_year:24*(day_of_the_year+num_days)])

print(f"\n{len(weather)}-hour weather forecast succesfully obtained:\n{weather} °C")

print("\n---------------------------------------")
print("2 - Get forecasted load")
print("---------------------------------------")

# (1-delta)*100 confidence interval
delta = 0.05
pred_load, min_pred_load, max_pred_load = load_forecast.get_forecast_CI(weather, best_forecaster, model, delta, path_to_past_data)
print(f"\nLoad succesfully predicted with {best_forecaster}, and {(1-delta)*100}% confidence interval obtained.")
print(f"{[round(x[0],2) for x in pred_load]} +/- {pred_load[0]-min_pred_load[0]} kWh")

print("\n---------------------------------------")
print("3 - Get HP commands from Pareto")
print("---------------------------------------")

# Select price forecast (options are: "GridWorks", "Progressive", "Peter")
price_forecast = "Peter"

# Temperature of water going to the HPs (Celcius)
T_HP_in = 55
# Minimum temperature of water going to the PCM (Celcius)
T_sup_HP_min = 58
# Maximum storage capacity (kWh)
max_storage = 30

# Get the operation over the forecsats
Q_HP, m_HP = pareto_algorithm.get_pareto(pred_load, price_forecast, weather, T_HP_in, T_sup_HP_min, max_storage, False, False, num_days)

print(f"\nObtained the solution from the pareto algorithm.\nQ_HP = {Q_HP}")

# Is the heat pump on or off
delta_HP = [0 if q==0 else 1 for q in Q_HP]
print(f"\nConverted Q_HP into commands for the FMU:\ndelta_HP = {delta_HP}")

# What temperature setpoint should we give it
T_sup_HP = [round(Q_HP[i]*1000/m_HP[i]/4187 + T_HP_in,1) if Q_HP[i]!=0 else np.nan for i in range(len(Q_HP))]
print(f"T_sup_HP = {T_sup_HP}")
    
print("\n---------------------------------------")
print("4 - Send commands to FMU and simulate")
print("---------------------------------------")

simulation_results = fmu_simulation.simulate(delta_HP, T_sup_HP, weather, num_days)
