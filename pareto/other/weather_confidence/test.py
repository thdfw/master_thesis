import pandas as pd
import numpy as np
import random
import os
import sys
import matplotlib.pyplot as plt

df_final = pd.DataFrame(list(range(17)), columns=['hours_in_future'])

# Iterate over all files in the directory
for file_name in sorted(os.listdir(os.getcwd()+'/forecasts')):
        
    df = pd.read_csv(os.getcwd()+f'/forecasts/{file_name}')
    
    if len(df) != 17: continue

    date, hour = file_name.split('_')[2].split("-")
    df_final[f'forecast_{date[6:8]}-{date[4:6]}-{hour[:2]}'] = list(df.temp_air)
        
df_final = df_final.drop('hours_in_future', axis = 1)
df_final = df_final.dropna(axis=1, how='any')

print(f"\nWe have {len(df_final.columns.to_list())} 16-hour forecasts.\n")
#display(df_final)

import datetime as dtm

# Function to gather data from database
def download_data(dt_start=dtm.datetime(2020,10,6,11,0),
                  dt_final=dtm.datetime.now()):
    
    # Specify specific exterior weather values to download
    channels = ['Exterior_we_Temperature_C']

    # Download data
    res = db.read_raw_db(dt_start, dt_final, channels)
    
    return res
    
# First and last dates in the data
dates = df_final.columns.to_list()
first_date = '2021-' + dates[0].split("_")[1] + ':00:00'
last_date = '2021-' + dates[-1].split("_")[1] + ':00:00'

# Convert to timestamps
format_string = "%Y-%d-%m-%H:%M:%S"
first_timestamp = dtm.datetime.strptime(first_date, format_string)
last_timestamp = dtm.datetime.strptime(last_date, format_string)
print(f"First timestamp: {first_timestamp}\nLast timestamp: {last_timestamp}")

# Log into database
sys.path.append(os.getcwd()+'/measurements/btrdb_api')
from client import client as btrdb

db = btrdb()
db.login_no_interactive('device1', '123456')

# Download data
monitored_data = download_data(dt_start = first_timestamp, dt_final = last_timestamp)
monitored_data = monitored_data.rename(columns={'Exterior_we_Temperature_C': 'T_OA'})
monitored_data = monitored_data[['T_OA']]

# Average hourly
measurement_hourly = monitored_data.resample('H').mean()
print(f"Succesfully loaded hourly weather measurements.")
display(measurement_hourly)
