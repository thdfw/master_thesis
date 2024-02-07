import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import datetime as dtm
import load_forecast, pareto_algorithm, fmu_simulation, weather_forecast

print("\n---------------------------------------")
print("0 - Find the best forecaster [Need to use fcSelector]")
print("---------------------------------------")

# Get past data
path_to_past_data = os.getcwd()+'/data/gridworks_yearly_data.xlsx'
past_data = load_forecast.get_past_data(path_to_past_data)

# Find the forecaster that performs best on past data
best_forecaster, model = load_forecast.get_best_forecaster(past_data, path_to_past_data)

print(f"\nThe forecaster that performed best on the past data is {best_forecaster}.")

print("\n---------------------------------------")
print("1 - Import weather forecast [Check forecast length]")
print("---------------------------------------")

# Get forecast for Maine (= None for live forecast)
start = None
end = None
start = dtm.datetime(2024, 2, 4, 0, 0, 0)
end = dtm.datetime(2024, 2, 4, 23, 0, 0)
weather, CI_weather = weather_forecast.get_weather(start, end)
#weather = weather[:17]

# Lenght of simulation (hours)
num_hours = len(weather)

# To use GridWorks past data instead
#df = pd.read_excel(os.getcwd()+'/data/gridworks_yearly_data.xlsx', header=3, index_col = 0)
#df.index = pd.to_datetime(df.index)
#df.index.name = None
#df['Outside Temp F'] = df['Outside Temp F'].apply(lambda x: round(5/9 * (x-32),2))
#day_of_the_year = 60
#weather = list(df['Outside Temp F'][24*day_of_the_year:24*(day_of_the_year+num_days)])

print(f"\n{num_hours}-hour weather forecast succesfully obtained, with 95% confidence interval.")
print(f"{weather} \n+/- {CI_weather[:num_hours]}°C")

print("\n---------------------------------------")
print("2 - Get forecasted load [OK]")
print("---------------------------------------")

# Predict load with 95% confidence interval for predicted weather
delta = 0.05
pred_load, min_pred_load, max_pred_load = load_forecast.get_forecast_CI(weather, best_forecaster, model, delta, path_to_past_data)
print(f"\nLoad succesfully predicted with {best_forecaster}, with {round((1-delta)*100)}% confidence interval.")
print(f"{[round(x[0],2) for x in pred_load]} \n+/- {pred_load[0]-min_pred_load[0]} kWh")

# Predict load with 95% confidence interval for coldest predicted weather (weather - CI)
min_weather = [round(weather[i]-CI_weather[i],2) for i in range(num_hours)]
pred_max_load, min_pred_max_load, max_pred_max_load = load_forecast.get_forecast_CI(min_weather, best_forecaster, model, delta, path_to_past_data)

# The final confidence interval for the load is CI(forecast->weather) + CI(weater->load)
final_CI = [max_pred_max_load[i]-pred_load[i] if CI_weather[i]>0 else [0] for i in range(num_hours)]
final_CI = [round(x[0],2) for x in final_CI]
print(f"\nCombining with weather confidence interval:")
print(f"{[round(x[0],2) for x in pred_load]} \n+/- {final_CI} kWh")

print("\n---------------------------------------")
print("3 - Get HP commands from Pareto [OK]")
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
Q_HP, m_HP = pareto_algorithm.get_pareto(pred_load, price_forecast, weather, T_HP_in, T_sup_HP_min, max_storage, False, False, num_hours, final_CI)

print(f"\nObtained the solution from the pareto algorithm.\nQ_HP = {Q_HP}")

# Is the heat pump on or off
delta_HP = [0 if q==0 else 1 for q in Q_HP]
print(f"\nConverted Q_HP into commands for the FMU:\ndelta_HP = {delta_HP}")

# What temperature setpoint should we give it
T_sup_HP = [round(Q_HP[i]*1000/m_HP[i]/4187 + T_HP_in,1) if Q_HP[i]!=0 else np.nan for i in range(len(Q_HP))]
print(f"T_sup_HP = {T_sup_HP}")
    
print("\n---------------------------------------")
print("4 - Send commands to FMU and simulate [Check Dymola license]")
print("---------------------------------------")

simulation_results = fmu_simulation.simulate(delta_HP, T_sup_HP, weather, num_hours)
