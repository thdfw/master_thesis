'''
This file is to obtain the forecasts for electricty prices and loads between in a given time frame.
For both functions, the inputs are the desired start and end time steps.
'''

# Get all electricity prices
def get_c_el(start, end, delta_t_h):

    # Electricity prices in cts/kWh, hourly prices for 24 hours
    c_el_all = [18.97, 18.92, 18.21, 16.58, 16.27, 15.49, 14.64, 18.93, 45.56, 26.42, 18.0, 17.17, 16.19, 30.74, 31.17, 16.18, 17.11, 20.24, 24.94, 24.69, 26.48, 30.15, 23.14, 24.11]
    
    # The number of time steps that make up one hour
    try: time_steps = int(1/delta_t_h)
    except: raise ValueError("The chosen time step does not add up to an hour.")
    
    # Extend to match time step (1 hour is 1/delta_t_h time steps)
    c_el_all = [item for item in c_el_all for _ in range(time_steps)]
        
    # Convert to $/Wh
    c_el_all = [x/100/1000 for x in c_el_all]
    
    # Duplicate daily data
    c_el_all = c_el_all*30
    
    return c_el_all[start:end]


# Get all loads
def get_m_load(start, end, delta_t_h):

    # Loads in Wh (this is not the final data)
    Q_load_all = [310]*1000
    
    # Some constants
    cp = 4187
    Delta_T_load = 5/9*20
    
    # Corresponding mass flow rates in kg/s
    m_load_all = [Q_load/(delta_t_h*cp*Delta_T_load) for Q_load in Q_load_all]
    
    return m_load_all[start:end]
