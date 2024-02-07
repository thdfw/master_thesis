import os
import sys
import time
import pytz
import warnings
import numpy as np
import pandas as pd
import datetime as dtm
import matplotlib.pyplot as plt
from pvlib.forecast import HRRR

PRINT = False
PLOT = False

def get_forecast_pvlib(lat, lon, start_time, final_time):

    forecaster = HRRR()
    query_variables = list(forecaster.variables.values())
    query_variables.remove('Temperature_height_above_ground')
    query_variables.remove('v-component_of_wind_height_above_ground')
    query_variables.remove('u-component_of_wind_height_above_ground')

    wf1 = forecaster.get_data(lat, lon, start_time, final_time,
                              query_variables=query_variables)

    forecaster = HRRR()
    wf2 = forecaster.get_data(lat, lon, start_time, final_time,
                              query_variables=['Temperature_height_above_ground'])

    wf = pd.concat([wf1, wf2], axis=1)
    return wf

class weather_forecaster(object):

    # Initialize Maine lat, long, time zone, irradiance, horizon, model
    def __init__(self, latitude=45.367584, longitude=-68.972168, tz='America/New_York',
                 irrad_vars=['ghi', 'dni', 'dhi'], horizon=24, model=HRRR):
        
        self.latitude = latitude
        self.longitude = longitude
        self.tz = tz
        self.irrad_vars = irrad_vars
        self.horizon = horizon
        self.forecaster = model()
        
    def get_forecast(self, start=None, end=None):

        # If no start time is provided, choose now (converted to timezone)
        if not start:
            start = dtm.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            self.start_dt = pd.Timestamp(start, tz='UTC').tz_convert(self.tz)
            if PRINT:
                print(f"Current UTC time: {start}")
                print(f"Current time in {self.tz}: {self.start_dt}")
                print("")
            
        # Otherwise read the provided start time
        else:
            self.start_dt = pd.Timestamp(start, tz=self.tz)
        
        # If no end time is provided, choose now + horizon
        if not end:
            self.end_dt = self.start_dt + pd.Timedelta(hours=self.horizon)
        # Otherwise read th provided end time
        else:
            self.end_dt = pd.Timestamp(end, tz=self.tz)
            
        # Get the forecast from pvlib
        self.forecast = get_forecast_pvlib(self.latitude, self.longitude, self.start_dt, self.end_dt)
        
        # Set the forecast of some columns to 0
        dummy_forecast_cols = ['wind_speed_u', 'wind_speed_v',
                       'Low_cloud_cover_low_cloud', 'Medium_cloud_cover_middle_cloud', 'High_cloud_cover_high_cloud',
                       'Pressure_surface', 'Wind_speed_gust_surface']
        for c in dummy_forecast_cols:
            self.forecast[c] = 0

        # Set the location
        self.forecaster.set_location(self.start_dt.tz, self.latitude, self.longitude)
        
        # Process data
        # Duplicate last beacuse of bug in pvlib
        self.forecast.loc[self.forecast.index[-1]+pd.DateOffset(hours=1), :] = self.forecast.iloc[-1]
        self.data = self.forecaster.process_data(self.forecast)
        self.data = self.data.loc[self.forecast.index[:-1]]
        self.data.index = self.data.index.tz_localize(None)
                              
        return list(self.data['temp_air'])


def get_weather(start, end):

    # Initialize
    forecaster = weather_forecaster()

    # Get the forecast
    T_OA_list = forecaster.get_forecast(start, end)
    
    # Confidence intervals from past data
    CIs = [2.4102025555533313, 2.313273333333333, 2.353639999995, 2.228993777773333, 2.5042659999999994, 2.332507777778334, 2.675285666668332, 2.520124333326665, 2.5709882222183325, 2.6398711111166655, 2.678220333335002, 2.7022454444466675, 2.7966293333350016, 3.001692444445002, 2.827686777780002, 3.0397588888849985, 2.757263333331668]
    
    # Fill in CI with np.nan
    if len(T_OA_list) > len(CIs):
        CIs = CIs + [0]*(len(T_OA_list)-len(CIs))
    
    if PLOT:
        length = len(CIs) if len(CIs)<len(T_OA_list) else len(T_OA_list)
        
        # Plot the weather with the confidence interval
        lower_bounds = [T_OA_list[i] - CIs[i] for i in range(length)]
        upper_bounds = [T_OA_list[i] + CIs[i] for i in range(length)]
        plt.plot(T_OA_list, color='red', alpha=0.6, label='pvlib forecast')
        plt.fill_between(range(length), lower_bounds, upper_bounds, color='red', alpha=0.1, label='90% confidence interval')
        plt.xlabel("Hour")
        plt.ylabel("Outside air temperature (°C)")
        plt.xticks(list(range(length)))
        plt.legend()
        plt.show()

    return [round(x,2) for x in T_OA_list], [round(x,2) for x in CIs]
