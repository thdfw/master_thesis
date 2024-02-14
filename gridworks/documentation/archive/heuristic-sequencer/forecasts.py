import numpy as np

'''
Input: index of desired start and end time steps
Output: list of forecasted electricty prices between start and end time steps
'''
def get_c_el(start, end, delta_t_h):

    # Hourly electricity prices in cts/kWh (24 hours) - cluster 4
    c_el_all = [6.36, 6.34, 6.34, 6.37, 6.41, 6.46, 6.95, 41.51,
    41.16, 41.07, 41.06, 41.08, 7.16, 7.18, 7.18, 7.16, 41.2,
    41.64, 41.43, 41.51, 6.84, 6.65, 6.46, 6.4]
    
    # The good old prices
    c_el_all = [18.97, 18.92, 18.21, 16.58, 16.27, 15.49, 14.64,
    18.93, 45.56, 26.42, 18.0, 17.17, 16.19, 30.74, 31.17, 16.18,
    17.11, 20.24, 24.94, 24.69, 26.48, 30.15, 23.14, 24.11]
    
    # Sudden negative price announced at 2 AM
    # if start >= 15*2 or (start == 0 and end==15*24): c_el_all[2] = -15

    # Extend to match time step (1 hour is 1/delta_t_h time steps)
    time_steps = int(1/delta_t_h)
    c_el_all = [item for item in c_el_all for _ in range(time_steps)]
        
    # Convert cts/kWh to $/Wh
    c_el_all = [x/100/1000 for x in c_el_all]
    
    # Duplicate day
    c_el_all = c_el_all*3
    
    return c_el_all[start:end]

'''
Input: index of desired start and end time steps
Output: list of forecasted load mass flow rates between start and end time steps
'''
def get_m_load(start, end, delta_t_h):

    # Hourly average heating power in kW
    Q_load_all = [5.91, 5.77, 5.67, 5.77, 5.71, 6.06, 6.34, 6.34,
    6.01, 5.77, 5.05, 5.05, 4.91, 4.91, 4.91, 4.91, 5.05, 5.1,
    4.91, 4.91, 4.91, 4.91, 4.98, 4.91]
        
    # Corresponding load mass flow rates in kg/s
    cp, Delta_T_load = 4187,  5/9*20
    m_load_all = [round(Q_load*1000/(cp*Delta_T_load), 3) for Q_load in Q_load_all]
    
    # High cluster
    #m_load_all = [0.16, 0.16, 0.16, 0.16, 0.16, 0.16, 0.16, 0.16, 0.15, 0.14, 0.14, 0.13, 0.13, 0.13, 0.13, 0.13, 0.14, 0.14, 0.14, 0.15, 0.15, 0.15, 0.15, 0.15]

    # intermediate cluster
    m_load_all = [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.1, 0.1, 0.08, 0.08, 0.08, 0.08, 0.08, 0.07, 0.07, 0.07, 0.07, 0.07, 0.09, 0.09, 0.1, 0.1, 0.11, 0.11]
    
    # Intermediate load until 4PM, after no more load
    # m_load_all = [0.1]*16 + [0]*8
    
    # low cluster
    # m_load_all = [0.05, 0.04, 0.04, 0.05, 0.05, 0.04, 0.04, 0.03, 0.02, 0.01, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.02, 0.02, 0.04, 0.04, 0.04, 0.05]
    
    # Extend to match time step (1 hour is 1/delta_t_h time steps)
    m_load_all = [item for item in m_load_all for _ in range(int(1/delta_t_h))]
        
    # Duplicate day
    m_load_all = m_load_all*3
    
    return m_load_all[start] if end-start==1 else m_load_all[start:end]
    
'''
Input: index of desired start and end time steps
Output: list of forecasted 1/COP and Q_HP_max between these time steps, based on T_OA forecast
'''
def get_T_OA(start, end, delta_t_h):
    
    # Outside air temperature in K
    T_OA_all = [273+12]*1000

    # Get 1/COP from the T_OA with linear regression
    B0_C, B1_C = 2.695868, -0.008533
    COP1_all = [round(B0_C + B1_C*T_OA_all[i],4) for i in range(len(T_OA_all))]

    # Get Q_HP_max from the T_OA with linear regression
    B0_Q, B1_Q = -68851.589, 313.3151
    Q_HP_max_all = [round(B0_Q + B1_Q*T_OA_all[i],2) if T_OA_all[i]<(273-7) else 14000 for i in range(len(T_OA_all))]
    
    return COP1_all[start:end], Q_HP_max_all[start:end]
