def functions_exact_sym(id,u,x):

    # Mass flow rate at buffer tank
    m_buffer_sym = (m_HP * case['HP'] - u_sym[1] * (2*case['ch']-1) - m_load) / (2 * case['bu'] - 1)

    # Temperatures entering and exiting the load
    T_sup_load_sym = (m_HP*u_sym[0]*case['HP'] + u_sym[1]*x_sym[4]*(1-case['ch']) + m_buffer_sym*x_sym[0]*(1-case['bu'])) / (m_HP*case['HP'] + u_sym[1]*(1-case['ch']) + m_buffer_sym*(1-case['bu']))
    T_ret_load_sym = T_sup_load_sym - Delta_T_load

    # Temperature entering the heat pump
    T_ret_HP_sym = (m_load*T_ret_load_sym + u_sym[1]*x_sym[15]*case['ch'] + m_buffer_sym*x_sym[3]*case['bu']) / (m_load + u_sym[1]*case['ch'] + m_buffer_sym*case['bu'])

    # Intermediate temperatures
    T_HP_stor_sym = (m_HP*u_sym[0]*case['HP'] + u_sym[1]*x_sym[4]*(1-case['ch'])) / (m_HP*case['HP'] + u_sym[1]*(1-case['ch']))
    T_ret_load_buffer_sym = (m_load*T_ret_load_sym + m_buffer_sym*x_sym[3]*case['bu']) / (m_load + m_buffer_sym*case['bu'])

    # The functions to approximate
    functions_sym = {
        # Objective and constraints [ok]
        "Q_HP":         m_HP * cp * (u_sym[0] - T_ret_HP_sym) * case['HP'],
        "T_sup_load_sym":   T_sup_load_sym,
        "m_buffer_sym":     m_buffer_sym,
            
        # --- Buffer tank --- Convection [ok]
        "Q_conv_B1":    m_buffer_sym * cp * (x_sym[1] - x_sym[0]),
        "Q_conv_B2":    m_buffer_sym * cp * (x_sym[0] - 2*x_sym[1] + x_sym[2]),
        "Q_conv_B3":    m_buffer_sym * cp * (x_sym[1] - 2*x_sym[2] + x_sym[3]),
        "Q_conv_B4":    m_buffer_sym * cp * (x_sym[2] - x_sym[3]),
        
        # --- Buffer tank --- Top and Bottom [ok]
        "Q_top_B":     case['bu']     * m_buffer_sym * cp * (T_HP_stor_sym - x_sym[0]),
        "Q_bottom_B":  (1-case['bu']) * m_buffer_sym * cp * (T_ret_load_sym - x_sym[3]),
        
        # --- Storage taks --- Convection [ok]
        "Q_conv_S11":   u_sym[1] * cp * (x_sym[5] - x_sym[4]),
        "Q_conv_S12":   u_sym[1] * cp * (x_sym[4] - 2*x_sym[5] + x_sym[6]),
        "Q_conv_S13":   u_sym[1] * cp * (x_sym[5] - 2*x_sym[6] + x_sym[7]),
        "Q_conv_S14":   u_sym[1] * cp * (x_sym[6] - x_sym[7]),
        
        "Q_conv_S21":   u_sym[1] * cp * (x_sym[9] - x_sym[8]),
        "Q_conv_S22":   u_sym[1] * cp * (x_sym[8] - 2*x_sym[9] + x_sym[10]),
        "Q_conv_S23":   u_sym[1] * cp * (x_sym[9] - 2*x_sym[10] + x_sym[11]),
        "Q_conv_S24":   u_sym[1] * cp * (x_sym[10] - x_sym[11]),
        
        "Q_conv_S31":   u_sym[1] * cp * (x_sym[13] - x_sym[12]),
        "Q_conv_S32":   u_sym[1] * cp * (x_sym[12] - 2*x_sym[13] + x_sym[14]),
        "Q_conv_S33":   u_sym[1] * cp * (x_sym[13] - 2*x_sym[14] + x_sym[15]),
        "Q_conv_S34":   u_sym[1] * cp * (x_sym[14] - x_sym[15]),

        # --- Storage tanks --- Top and Bottom [ok]
        "Q_top_S1":    case['ch'] * u_sym[1] * cp * (u_sym[0] - x_sym[4]),
        "Q_top_S2":    case['ch'] * u_sym[1] * cp * (x_sym[7] - x_sym[8]),
        "Q_top_S3":    case['ch'] * u_sym[1] * cp * (x_sym[11] - x_sym[12]),
        "Q_bottom_S1": (1-case['ch']) * u_sym[1] * cp * (x_sym[8] - x_sym[7]),
        "Q_bottom_S2": (1-case['ch']) * u_sym[1] * cp * (x_sym[12] - x_sym[11]),
        "Q_bottom_S3": (1-case['ch']) * u_sym[1] * cp * (T_ret_load_buffer_sym - x_sym[15]),
    }

    return functions_sym[id]
