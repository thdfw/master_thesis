'''
This file is to obtain the forecasts for electricty prices and loads.
For both functions, the inputs are the desired start and end time steps.
'''

# Get all electricity prices
def get_c_el(start,end):

    # Electricity prices in cts/kWh
    c_el_all = [12] + [2] + [55] + [18.97]*12 + [18.92]*3 + [11]*9 + [18.21]*12 + [16.58]*12 + [16.27]*12 + [15.49]*12 + [14.64]*12 + [18.93]*12 + [45.56]*12 + [26.42]*12 + [18.0]*12 + [17.17]*12 + [16.19]*12 + [30.74]*12 + [31.17]*12 + [16.18]*12 + [17.11]*12 + [20.24]*12 + [24.94]*12 + [24.69]*12 + [26.48]*12 + [30.15]*12 + [23.14]*12 + [24.11]*12
    c_el_all = c_el_all*30

    return c_el_all[start:end]

# Get all loads
def get_m_load(start,end):
    
    # Mass flow rate in kg/s
    m_load_all = [0.5]*1000
    
    return m_load_all[start:end]
