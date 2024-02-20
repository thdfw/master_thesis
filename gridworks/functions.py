import numpy as np
import forecasts

# Some constants
Delta_T_load = 5/9*20
cp = 4187
delta_t_h = 4/60

# For the denominators
epsilon = 1e-7

'''
Returns the value of the function called "id"
'''
def get_function(id, u, x, t, sequence, iter):

    # -----------------------------------------------
    # Get current combination and load mass flow rate
    # -----------------------------------------------
    
    # Get the section (1 to 8) at time t
    section = int(t/15)+1
    
    # Get current combination at time t
    combi = sequence[f'combi{section}']
    
    # Get load mass flow rate at time t
    start_forecast = int(iter+(section-1)/delta_t_h)
    m_load = forecasts.get_m_load(start_forecast, start_forecast+1, delta_t_h)
    
    # -----------------------------------------------
    # Define all variables
    # -----------------------------------------------
    
    # Get the delta terms corresponding to the combi
    delta_ch, delta_bu, delta_HP = combi
    delta_R = u[5]

    # Get the other variables from the inputs and states
    T_sup_HP, m_stor            = u[0], u[1]
    T_B1, T_B2, T_B3, T_B4      = x[0], x[1], x[2], x[3]
    T_S11, T_S12, T_S13, T_S14  = x[4], x[5], x[6], x[7]
    T_S21, T_S22, T_S23, T_S24  = x[8], x[9], x[10], x[11]
    T_S31, T_S32, T_S33, T_S34  = x[12], x[13], x[14], x[15]
    
    # -----------------------------------------------
    # All intermediate functions
    # -----------------------------------------------
    
    # Mass flow rate from HP
    # B_0M, B_1M = 4.2669, -0.0117 # variable m_HP
    B_0M, B_1M = 0.5, 0 # fixed m_HP
    m_HP = B_0M + B_1M * T_sup_HP

    # Mass flow rate at buffer tank
    m_buffer = (m_HP*delta_HP - m_stor*(2*delta_ch-1) - m_load) / (2*delta_bu-1)

    # Temperatures entering and exiting the load
    T_sup_load = (m_HP*T_sup_HP*delta_HP + m_stor*T_S11*(1-delta_ch) + m_buffer*T_B1*(1-delta_bu)) / (m_HP*delta_HP + m_stor*(1-delta_ch) + m_buffer*(1-delta_bu) + epsilon)
    T_ret_load = T_sup_load - Delta_T_load

    # Temperature entering the heat pump
    T_ret_HP = (m_load*T_ret_load + m_stor*T_S34*delta_ch + m_buffer*T_B4*delta_bu) / (m_load + m_stor*delta_ch + m_buffer*delta_bu + epsilon)

    # Intermediate temperatures
    T_HP_stor = (m_HP*T_sup_HP*delta_HP + m_stor*T_S11*(1-delta_ch)) / (m_HP*delta_HP + m_stor*(1-delta_ch) + epsilon)
    T_ret_load_buffer = (m_load*T_ret_load + m_buffer*T_B4*delta_bu) / (m_load + m_buffer*delta_bu + epsilon)

    # -----------------------------------------------
    # All functions which are explicity called
    # -----------------------------------------------
    
    # Objective and constraints [ok]
    if   id=="Q_HP":        return m_HP * cp * (T_sup_HP - T_ret_HP) * delta_HP
    elif id=="m_HP":        return m_HP
    elif id=="T_sup_load":  return T_sup_load
    elif id=="m_buffer":    return m_buffer
            
    # --- Buffer tank --- Convection [ok]
    elif id=="Q_conv_B1":   return (1-delta_bu) * (m_buffer * cp * (T_B2 - T_B1)) + delta_bu * 0
    elif id=="Q_conv_B2":   return (1-delta_bu) * (m_buffer * cp * (T_B3 - T_B2)) + delta_bu * (m_buffer * cp * (T_B1 - T_B2))
    elif id=="Q_conv_B3":   return (1-delta_bu) * (m_buffer * cp * (T_B4 - T_B3)) + delta_bu * (m_buffer * cp * (T_B2 - T_B3))
    elif id=="Q_conv_B4":   return (1-delta_bu) * 0                               + delta_bu * (m_buffer * cp * (T_B3 - T_B4))
        
    # --- Buffer tank --- Top and Bottom [ok]
    elif id=="Q_top_B":     return delta_bu     * m_buffer * cp * (T_HP_stor - T_B1)
    elif id=="Q_bottom_B":  return (1-delta_bu) * m_buffer * cp * (T_ret_load - T_B4)
        
    # --- Storage taks --- Convection [ok]
    elif id=="Q_conv_S11":  return (1-delta_ch) * (m_stor * cp * (T_S12 - T_S11)) + delta_ch * 0
    elif id=="Q_conv_S12":  return (1-delta_ch) * (m_stor * cp * (T_S13 - T_S12)) + delta_ch * (m_stor * cp * (T_S11 - T_S12))
    elif id=="Q_conv_S13":  return (1-delta_ch) * (m_stor * cp * (T_S14 - T_S13)) + delta_ch * (m_stor * cp * (T_S12 - T_S13))
    elif id=="Q_conv_S14":  return (1-delta_ch) * 0                               + delta_ch * (m_stor * cp * (T_S13 - T_S14))

    elif id=="Q_conv_S21":  return (1-delta_ch) * (m_stor * cp * (T_S22 - T_S21)) + delta_ch * 0
    elif id=="Q_conv_S22":  return (1-delta_ch) * (m_stor * cp * (T_S23 - T_S22)) + delta_ch * (m_stor * cp * (T_S21 - T_S22))
    elif id=="Q_conv_S23":  return (1-delta_ch) * (m_stor * cp * (T_S24 - T_S23)) + delta_ch * (m_stor * cp * (T_S22 - T_S23))
    elif id=="Q_conv_S24":  return (1-delta_ch) * 0                               + delta_ch * (m_stor * cp * (T_S23 - T_S24))

    elif id=="Q_conv_S31":  return (1-delta_ch) * (m_stor * cp * (T_S32 - T_S31)) + delta_ch * 0
    elif id=="Q_conv_S32":  return (1-delta_ch) * (m_stor * cp * (T_S33 - T_S32)) + delta_ch * (m_stor * cp * (T_S31 - T_S32))
    elif id=="Q_conv_S33":  return (1-delta_ch) * (m_stor * cp * (T_S34 - T_S33)) + delta_ch * (m_stor * cp * (T_S32 - T_S33))
    elif id=="Q_conv_S34":  return (1-delta_ch) * 0                               + delta_ch * (m_stor * cp * (T_S33 - T_S34))
        
    # --- Storage tanks --- Top and Bottom [ok]
    elif id=="Q_top_S1":    return delta_ch * m_stor * cp * (T_sup_HP - T_S11)
    elif id=="Q_top_S2":    return delta_ch * m_stor * cp * (T_S14 - T_S21)
    elif id=="Q_top_S3":    return delta_ch * m_stor * cp * (T_S24 - T_S31)
    elif id=="Q_bottom_S1": return (1-delta_ch) * m_stor * cp * (T_S21 - T_S14)
    elif id=="Q_bottom_S2": return (1-delta_ch) * m_stor * cp * (T_S31 - T_S24)
    elif id=="Q_bottom_S3": return (1-delta_ch) * m_stor * cp * (T_ret_load_buffer - T_S34)
        
    elif id=="T_ret_HP":    return T_ret_HP
    elif id=="m_HP":        return m_HP
