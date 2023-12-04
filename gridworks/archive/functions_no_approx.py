from sympy import symbols, diff
import numpy as np
import casadi
import math

# For the denominators
epsilon = 1e-7

# Some constants
m_load = 0.2
Delta_T_load = 5/9*20
cp = 4187

# Mass flow rate from HP
B_0M, B_1M = 0.5, 0 #4.2669, -0.0117

# ------------------------------------------------------
# Get a function with the current sequence and u, x
# ------------------------------------------------------
    
def get_function(id, u, x, a, real, approx, t, sequence):

    if t>=0  and t<15: combi = sequence['combi1']
    if t>=15 and t<30: combi = sequence['combi2']
    if t>=30 and t<45: combi = sequence['combi3']
    if t>=45 and t<60: combi = sequence['combi4']
    
    # Get the delta terms
    delta_ch, delta_bu, delta_HP = combi
    delta_R = 0

    # Get the other variables from the inputs and states
    T_sup_HP, m_stor            = u[0], u[1]
    T_B1, T_B2, T_B3, T_B4      = x[0], x[1], x[2], x[3]
    T_S11, T_S12, T_S13, T_S14  = x[4], x[5], x[6], x[7]
    T_S21, T_S22, T_S23, T_S24  = x[8], x[9], x[10], x[11]
    T_S31, T_S32, T_S33, T_S34  = x[12], x[13], x[14], x[15]
    
    # Mass flow rate from HP
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

    # The functions to approximate
    functions = {
        # Objective and constraints [ok]
        "Q_HP":         m_HP * cp * (T_sup_HP - T_ret_HP) * delta_HP,
        "T_sup_load":   T_sup_load,
        "m_buffer":     m_buffer,
            
        # --- Buffer tank --- Convection [ok]
        "Q_conv_B1":    (1-delta_bu) * (m_buffer * cp * (T_B2 - T_B1)) + delta_bu * 0,
        "Q_conv_B2":    (1-delta_bu) * (m_buffer * cp * (T_B3 - T_B2)) + delta_bu * (m_buffer * cp * (T_B1 - T_B2)),
        "Q_conv_B3":    (1-delta_bu) * (m_buffer * cp * (T_B4 - T_B3)) + delta_bu * (m_buffer * cp * (T_B2 - T_B3)),
        "Q_conv_B4":    (1-delta_bu) * 0                               + delta_bu * (m_buffer * cp * (T_B3 - T_B4)),
        
        # --- Buffer tank --- Top and Bottom [ok]
        "Q_top_B":     delta_bu     * m_buffer * cp * (T_HP_stor - T_B1),
        "Q_bottom_B":  (1-delta_bu) * m_buffer * cp * (T_ret_load - T_B4),
        
        # --- Storage taks --- Convection [ok]
        "Q_conv_S11":    (1-delta_ch) * (m_stor * cp * (T_S12 - T_S11)) + delta_ch * 0,
        "Q_conv_S12":    (1-delta_ch) * (m_stor * cp * (T_S13 - T_S12)) + delta_ch * (m_stor * cp * (T_S11 - T_S12)),
        "Q_conv_S13":    (1-delta_ch) * (m_stor * cp * (T_S14 - T_S13)) + delta_ch * (m_stor * cp * (T_S12 - T_S13)),
        "Q_conv_S14":    (1-delta_ch) * 0                               + delta_ch * (m_stor * cp * (T_S13 - T_S14)),
        
        "Q_conv_S21":    (1-delta_ch) * (m_stor * cp * (T_S22 - T_S21)) + delta_ch * 0,
        "Q_conv_S22":    (1-delta_ch) * (m_stor * cp * (T_S23 - T_S22)) + delta_ch * (m_stor * cp * (T_S21 - T_S22)),
        "Q_conv_S23":    (1-delta_ch) * (m_stor * cp * (T_S24 - T_S23)) + delta_ch * (m_stor * cp * (T_S22 - T_S23)),
        "Q_conv_S24":    (1-delta_ch) * 0                               + delta_ch * (m_stor * cp * (T_S23 - T_S24)),
        
        "Q_conv_S31":    (1-delta_ch) * (m_stor * cp * (T_S32 - T_S31)) + delta_ch * 0,
        "Q_conv_S32":    (1-delta_ch) * (m_stor * cp * (T_S33 - T_S32)) + delta_ch * (m_stor * cp * (T_S31 - T_S32)),
        "Q_conv_S33":    (1-delta_ch) * (m_stor * cp * (T_S34 - T_S33)) + delta_ch * (m_stor * cp * (T_S32 - T_S33)),
        "Q_conv_S34":    (1-delta_ch) * 0                               + delta_ch * (m_stor * cp * (T_S33 - T_S34)),
        
        # --- Storage tanks --- Top and Bottom [ok]
        "Q_top_S1":    delta_ch * m_stor * cp * (T_sup_HP - T_S11),
        "Q_top_S2":    delta_ch * m_stor * cp * (T_S14 - T_S21),
        "Q_top_S3":    delta_ch * m_stor * cp * (T_S24 - T_S31),
        "Q_bottom_S1": (1-delta_ch) * m_stor * cp * (T_S21 - T_S14),
        "Q_bottom_S2": (1-delta_ch) * m_stor * cp * (T_S31 - T_S24),
        "Q_bottom_S3": (1-delta_ch) * m_stor * cp * (T_ret_load_buffer - T_S34),
        
        "T_ret_HP": T_ret_HP,
        "m_HP": m_HP,
    }
        
    f = functions[id]
    
    return f
