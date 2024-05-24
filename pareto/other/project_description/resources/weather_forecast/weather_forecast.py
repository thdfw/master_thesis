import json
import grequests
import requests
import os
import pandas as pd
import time
from pvlib.forecast import HRRR
import datetime
import pytz

request_headers = {'Accept': 'application/json',
                   'Accept-Language': 'en-US'} 

class weather_forecaster_multiplelocations(object):
    '''
    This class reads gathers the weather forecasts at several locations on a specified frequency. By
    default it uses pvlib to reference NOAA's HRRR forecast model, and returns the temperature and
    solar irradiation values. It reads a configuration file that specifies the stations and sampling
    frequency. It's possible to include the Advanced Windows Testbed by specifying AWTB = True.
    '''
    
    def __init__(self, config_path, AWTB=True, horizon=48, model=HRRR, irrad_vars=['ghi', 'dni', 'dhi']):
        '''
        Reads the config file and creates lists of latitude/longitude coordinate and timezone for each
        station.
        
        Inputs:
        config_path: Path to the stored configuration file specifying stations to read from, sampling
                     frequency, and output file.
        AWTB: Specifies whether to include the Advanced Windows Testbed or not.
        horizon: Desired length of the forecast. As of Nov 2, 2021 HRRR can provide up to 48 hours
                 but pvlib only returns 16.
        model: The desired NOAA forecasting tool.
        irrad_vars: The solar irradiation values to include in the forecast.
        '''
        
        # Extract information from the configuration file
        self.config = json.load(open(path_config))
        self.locations = self.config['locations']
        self.irrad_vars = irrad_vars
        self.horizon = horizon
        self.forecaster = model()   
        
        # Initialize lists of coordinates and timezones for the stations
        self.coordinates = []
        self.tz = []

        # Get coordinates & timezone for each station, store them in attributes
        for station in self.locations:
            url = 'https://api.weather.gov/stations/{}'.format(station)
            grequest = [grequests.get(url, verify=requests.certs.where(), headers=request_headers, timeout = 5)]
            gresponse = grequests.map(grequest)[0]
            
            if gresponse is None: # If there's no response from weather.gov
                print('Could not obtain details for {}. Will continue trying every 5 minutes'.format(station))
                import time                
                while gresponse is None:
                    time.sleep(5*60)
                    grequest = [grequests.get(url, verify=requests.certs.where(), headers=request_headers, timeout = 5)]
                    gresponse = grequests.map(grequest)[0]            
            
            response = json.loads(gresponse.content)
            self.coordinates.append(response['geometry']['coordinates'])
            self.tz.append(response['properties']['timeZone'])
        
        # If including the Advanced Windows Testbed add corresponding coordinates and timezone
        if AWTB:
            self.locations.append('71t')
            self.coordinates.append([-122.2501, 37.8788])
            self.tz.append('America/Los_Angeles')
            
    def get_forecasts(self, now_str, start=None, end=None, save = False, return_result = True):
        '''
        Gathers forecasts for all stations listed in the config file. Returns forecasts as a dict of
        pandas dataframes. dict keys are station names.
        
        Inputs:
        now_str: String representation of the time that this function is called.
        start: User-specified start time for the forecast.
        end: User specified end time for the forecast.
        save: State whether or not to save the forecast as a .csv file.
        return_result: State whether or not to return the resulting dict of forecasts.
        '''
        
        # Initialize dictionary of forecasts if needed
        if return_result == True:
            result = {}
            
        # Iterate through all locations
        for i in range(len(self.locations)):
            
            # Gather information about the location
            station = self.locations[i]
            lon = self.coordinates[i][0]
            lat = self.coordinates[i][1]
            tz = self.tz[i]
            
            # Set forecast start and end times
            if not start:
                start_dt = pd.Timestamp(time.time(), tz=tz, unit='s').replace( \
                    minute=0, second=0, microsecond=0, nanosecond=0)
            else:
                start_dt = pd.Timestamp(start, tz=tz)
            if end:
                end_dt = end
            else:
                end_dt = start_dt + pd.Timedelta(hours=self.horizon)        

            # Forecast processing
            try:
                data = self.forecaster.get_processed_data(lat, lon, start_dt, end_dt)
                print('Successfully gathered forecast for {}.'.format(station))
            except requests.exceptions.ConnectionError as e:
                data = 'ERROR: Lost connection to weather.gov. {}'.format(e)
            except requests.exceptions.HTTPError as e:
                data = 'ERROR: An HTTP error occured. {}'.format(e)
            except requests.exceptions.URLRequired as e:
                data = 'ERROR: Invalid URL supplied. {}'.format(e)
            except requests.exceptions.TooManyRedirects as e:
                data = 'ERROR: Forecast request was redirected too many times. {}'.format(e)
            except requests.exceptions.ConnectTimeout as e:
                data = 'ERROR: Timed out while connecting to weather.gov. {}'.format(e)
            except requests.exceptions.ReadTimeout as e:
                data = 'ERROR: The weather.gov server did not return data in allowed time. {}'.format(e)
            except requests.exceptions.Timeout as e:
                data = 'ERROR: The weather forecast request timed out. {}'.format(e)
            except Exception as e:
                data = 'ERROR: An unexpected error occurred - {}'.format(e)                

            # Save the forecast information to a .csv file if specified
            if save == True:
                folder_output = os.path.join(root, station)
                if not os.path.exists(folder_output):
                    os.mkdir(folder_output)                
                    
                path_output = os.path.join(folder_output, 'Forecast_{}_{}.csv'.format(station, now_str))
                data.to_csv(path_output)
                
            # Add forecast information to the dictionary if specified
            if return_result == True:
                result[station] = data
        
        # Return the forecast dictionary if specified
        if return_result == True:
            return result
            
    def run_daq(self, save, return_result):
        '''
        Repeatedly runs get_forecasts() on the user-specified frequency.
        '''
        
        while True:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
            before = time.time()
            try:
                self.get_forecasts(now_str, save, return_result)
                print('Successfully gathered forecasts at {}'.format(now_str))
            except Exception as e:
                print(e)
                print('ERROR at', datetime.datetime.now())
                
            after = time.time()
            
            # Calculate how long this process took, sleep until the next iteration starts
            time_elapsed = after - before
            time.sleep(float(self.config['poll_interval']) - time_elapsed) 

class weather_forecaster_singlelocation(object):
    '''
    This class  gathers the weather forecasts at one station on a specified frequency. By
    default it uses pvlib to reference NOAA's HRRR forecast model, and returns the temperature and
    solar irradiation values. It reads a configuration file that specifies the station and sampling
    frequency. It's possible to use the Advanced Windows Testbed by specifying AWTB = True. Doing so
    turns off other station locations.
    '''
    
    def __init__(self, config, coordinates = False, AWTB=False, horizon=48, model=HRRR, irrad_vars=['ghi', 'dni', 'dhi']):
        '''
        Reads the config information and finds latitude, longitude, and timezone for the specified location.
        
        Inputs:
        config: The configuration file specifying the target location, sampling frequency, and output file.
        coordinates: Specifies that the user provided a config file with specific location coordinates
                     instead of a weather.gov.
        AWTB: Specifies whether to use the Advanced Windows Testbed or not.
        horizon: Desired length of the forecast. As of Nov 2, 2021 HRRR can provide up to 48 hours
                 but pvlib only returns 16.
        model: The desired NOAA forecasting tool.
        irrad_vars: The solar irradiation values to include in the forecast.
        '''
        
        # Set the forecast information
        self.irrad_vars = irrad_vars
        self.horizon = horizon
        self.forecaster = model()
        
        # Store configuration information
        self.config = config
        
        # If using the Advanced Windows Testbed use the corresponding coordinates and timezone
        if AWTB:
            self.location = '71t'
            self.coordinates = [-122.2501, 37.8788]
            self.tz = pytz.timezone("Etc/GMT+8")
        
        # If using coordinates read them from coordinates and timezone from the configuration data
        elif coordinates:
            self.location = self.config['location']
            self.coordinates = config['coordinates']
            self.tz = pytz.timezone(config['timezone'])
            
        # If specifying location via a weather.gov weather station
        else:
            self.location = self.config['location']

            # Get coordinates & timezone for station, store them in attributes
            url = 'https://api.weather.gov/stations/{}'.format(self.location)
            grequest = [grequests.get(url, verify=requests.certs.where(), headers=request_headers, timeout = 5)]
            gresponse = grequests.map(grequest)[0]
            
            if gresponse is None: # If there's no response from weather.gov
                print('Could not obtain station details. Will continue trying every 5 minutes')
                # Try to obtain station details until successful
                while gresponse is None:
                    import time
                    time.sleep(5*60)
                    grequest = [grequests.get(url, verify=requests.certs.where(), headers=request_headers, timeout = 5)]
                    gresponse = grequests.map(grequest)[0]
            
            response = json.loads(gresponse.content)
            self.coordinates = response['geometry']['coordinates']
            self.tz = response['properties']['timeZone']        

    def get_forecasts(self, now_str = 'N/A', start = None, end = None, save = False, return_result = False, json_output = False):
        '''
        Gathers forecasts for the specified station. Returns either the forecast or an
        error message as appropriate
        
        Inputs:
        now_str: String representation of the time that this function is called.
        start: User-specified start time for the forecast.
        end: User specified end time for the forecast.
        save: State whether or not to save the forecast as a .csv file.
        return_result: State whether or not to return the resulting forecast. By default
                       returns a pandas dataframe.
        json_output: Converts the output from a pandas dataframe to json.
        '''

        # Gather information about the location
        station = self.location
        lon = self.coordinates[0]
        lat = self.coordinates[1]
        tz = self.tz
            
        # Set forecast start and end times
        if not start:
            start_dt = pd.Timestamp(datetime.datetime.now().replace(minute=0, second=0, microsecond = 0), tzinfo = tz)
        else:
            start_dt = pd.Timestamp(start, tz=tz)
        if end:
            end_dt = end
        else:
            end_dt = start_dt + pd.Timedelta(hours=self.horizon)        

        # Forecast processing
        expected_index = pd.date_range(start_dt, end_dt, freq = 'H')
        data = pd.DataFrame(index = expected_index, columns = ['temp_air', 'wind_speed', 'ghi', 
                                                               'dni', 'dhi', 'total_clouds',
                                                               'low_clouds', 'mid_clouds', 
                                                               'high_clouds'])
        error_msg = None
        
        try:
            data = self.forecaster.get_processed_data(lat, lon, start_dt, end_dt)

        except requests.exceptions.ConnectionError as e:
            error_msg = 'ERROR: Lost connection to weather.gov. {}'.format(e)
        except requests.exceptions.HTTPError as e:
            error_msg = 'ERROR: An HTTP error occured. {}'.format(e)
        except requests.exceptions.URLRequired as e:
            error_msg = 'ERROR: Invalid URL supplied. {}'.format(e)
        except requests.exceptions.TooManyRedirects as e:
            error_msg = 'ERROR: Forecast request was redirected too many times. {}'.format(e)
        except requests.exceptions.ConnectTimeout as e:
            error_msg = 'ERROR: Timed out while connecting to weather.gov. {}'.format(e)
        except requests.exceptions.ReadTimeout as e:
            error_msg = 'ERROR: The weather.gov server did not return data in allowed time. {}'.format(e)
        except requests.exceptions.Timeout as e:
            error_msg = 'ERROR: The weather forecast request timed out. {}'.format(e)
        except Exception as e:
            error_msg = 'ERROR: An unexpected error occurred - {}'.format(e)

        # Save the forecast information to a .csv file if specified
        if save == True:
            folder_output = os.path.join(root, station)
            if not os.path.exists(folder_output):
                os.mkdir(folder_output)                
                    
            path_output = os.path.join(folder_output, 'Forecast_{}_{}.csv'.format(self.location, now_str))
            data.to_csv(path_output)
            
        # Return the forecast dictionary if specified
        if return_result == True:
            if json_output:
                data.index = data.index.tz_localize(None)
                return data.to_json(), error_msg
            else:
                return data, error_msg
            
    def run_daq(self, save = False, return_result = False, json_output = False):
        '''
        Repeatedly runs get_forecasts() on the user-specified frequency.
        '''

        while True:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
            before = time.time()
            try:
                forecast = self.get_forecasts(now_str = now_str, save = save, return_result = return_result, 
                                              json_output = json_output)
                
                if type(forecast) == str: 
                    print(forecast)
                else:
                    print('Successfully gathered forecast at {}'.format(now_str))
            except Exception as e:
                print(e)
                print('Error at {}'.format(now_str))
                
            after = time.time()
            
            # Calculate how long this process took, sleep until the next iteration starts
            time_elapsed = after - before
            time.sleep(float(self.config['poll_interval']) - time_elapsed)             
            
if __name__ == '__main__':
    
    # Run both _singlelocation and _multiplelocations one time
    try:
        root = os.path.dirname(os.path.realpath(__file__))
    except:
        root = os.getcwd()
        
    # Single location
    path_config = root + r'\forecasts_config_singlelocation'
    config = json.load(open(path_config))
    
    forecaster = weather_forecaster_singlelocation(config, coordinates = True)
    
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    
    result, error_msg = forecaster.get_forecasts(now_str = now, save = False, return_result = True, json_output = False)  
    
    print('single forecast')
    print(result)

    # Multiple locations
    path_config = os.path.join(root, 'forecasts_config_multiplelocations')
    
    forecaster = weather_forecaster_multiplelocations(path_config)
    
    result = forecaster.get_forecasts(now_str = now, return_result = True)
    
    print('multiple forecasts')
    print(result)