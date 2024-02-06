import os
import sys
import time
import pytz
import warnings
import numpy as np
import pandas as pd
import datetime as dtm
from pvlib.forecast import HRRR

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
            start = dtm.datetime.now().replace(minute=0, second=0, microsecond=0)
            self.start_dt = pd.Timestamp(start, tz='UTC').tz_convert(self.tz)

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
    
    return T_OA_list
