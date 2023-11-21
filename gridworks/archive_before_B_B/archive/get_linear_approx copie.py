from sympy import symbols, diff
import numpy as np
import casadi
import math

# -----
# Compute gradients for all function IDs
# -----

# Define all variables as symbols
T_sup_HP, m_stor = symbols('T_sup_HP m_stor')
delta_ch, delta_bu, delta_HP, delta_R = symbols('delta_ch delta_bu delta_hp delta_R')
T_B1, T_B2, T_B3, T_B4 = symbols('T_B1 T_B2 T_B3 T_B4')
T_S11, T_S12, T_S13, T_S14, T_S21, T_S22, T_S23, T_S24, T_S31, T_S32, T_S33, T_S34 \
= symbols('T_S11 T_S12 T_S13 T_S14 T_S21 T_S22 T_S23 T_S24 T_S31 T_S32 T_S33 T_S34')

# Gather all the symbols in a list
all_variables = [T_sup_HP, m_stor, delta_ch, delta_bu, delta_HP, delta_R,
T_B1, T_B2, T_B3, T_B4, T_S11, T_S12, T_S13, T_S14, T_S21, T_S22, T_S23, T_S24, T_S31, T_S32, T_S33, T_S34]




'''
GOAL:
Get the first order Taylor expansion (linear approximation) of a function f around a point "a"
Evaluate the value of the function and the approximation at a point "y"

INPUTS:
- id: The function we want (e.g. id=Q_HP if we want the function Q_HP)
- a = [a_u, a_x] is the point around which we linearize the function
    a_u is the component for the inputs "u"
    a_x is the component for the states "x"
- y = [y_u, y_x] is the point at which we want to get the function value
    y_u is the component for the inputs "u"
    y_x is the component for the states "x"
- real: True if y is real, False if y is symbolic (casadi terms)

OUTPUTS:
Returns a dictionnary with:
- Exact: f(y)
- Approx: f_approx(y)
- Rel_error: the relative error of the approximation
'''

def f_approx(id, a_u, a_x, y_u, y_x, real):

    # ------------------------------------------------------
    # Define variables and construct vectors
    # ------------------------------------------------------

    # Define all variables as symbols
    T_sup_HP, m_stor = symbols('T_sup_HP m_stor')
    delta_ch, delta_bu, delta_HP, delta_R = symbols('delta_ch delta_bu delta_hp delta_R')
    T_B1, T_B2, T_B3, T_B4 = symbols('T_B1 T_B2 T_B3 T_B4')
    T_S11, T_S12, T_S13, T_S14, T_S21, T_S22, T_S23, T_S24, T_S31, T_S32, T_S33, T_S34 \
    = symbols('T_S11 T_S12 T_S13 T_S14 T_S21 T_S22 T_S23 T_S24 T_S31 T_S32 T_S33 T_S34')
    
    # Gather all the symbols in a list
    all_variables = [T_sup_HP, m_stor, delta_ch, delta_bu, delta_HP, delta_R,
    T_B1, T_B2, T_B3, T_B4, T_S11, T_S12, T_S13, T_S14, T_S21, T_S22, T_S23, T_S24, T_S31, T_S32, T_S33, T_S34]
    
    # Construct "a" from given data
    a = {T_sup_HP: a_u[0], m_stor: a_u[1], delta_ch: a_u[2], delta_bu: a_u[3], delta_HP: a_u[4], delta_R: a_u[5],
    T_B1:  a_x[0],  T_B2:  a_x[1],  T_B3:  a_x[2],  T_B4:  a_x[3],
    T_S11: a_x[4],  T_S12: a_x[5],  T_S13: a_x[6],  T_S14: a_x[7],
    T_S21: a_x[8],  T_S22: a_x[9],  T_S23: a_x[10], T_S24: a_x[11],
    T_S31: a_x[12], T_S32: a_x[13], T_S33: a_x[14], T_S34: a_x[15]}

    # Construct "y" from given data
    if real:
        y = {T_sup_HP: y_u[0], m_stor: y_u[1], delta_ch: y_u[2], delta_bu: y_u[3], delta_HP: y_u[4], delta_R: y_u[5],
        T_B1:  y_x[0],  T_B2:  y_x[1],  T_B3:  y_x[2],  T_B4:  y_x[3],
        T_S11: y_x[4],  T_S12: y_x[5],  T_S13: y_x[6],  T_S14: y_x[7],
        T_S21: y_x[8],  T_S22: y_x[9],  T_S23: y_x[10], T_S24: y_x[11],
        T_S31: y_x[12], T_S32: y_x[13], T_S33: y_x[14], T_S34: y_x[15]}
    else:
        y = casadi.vertcat(y_u,y_x)
    
    # Some constants
    m_load = 0.2
    Delta_T_load = 5/9 * 20
    m_HP = 0.5
    cp = 4187

    # ------------------------------------------------------
    # Useful functions
    # ------------------------------------------------------

    # Mass flow rate at buffer tank
    m_buffer = (m_HP * delta_HP - m_stor * (2 * delta_ch - 1) - m_load) / (2 * delta_bu - 1)
    
    # Mixing temperatures
    T_sup_load = (m_HP*T_sup_HP*delta_HP + m_stor*T_S11*(1-delta_ch) + m_buffer*T_B1*(1-delta_bu)) / (m_HP*delta_HP + m_stor*(1-delta_ch) + m_buffer*(1-delta_bu))
    T_ret_load = T_sup_load - Delta_T_load
    T_ret_HP = (m_load*T_ret_load + m_stor*T_S34*delta_ch + m_buffer*T_B4*delta_bu) / (m_load + m_stor*delta_ch + m_buffer*delta_bu)

    # TEST
    T_sup_load_no_buffer = (m_HP*T_sup_HP*delta_HP + m_stor*T_S11*(1-delta_ch)) / (m_HP*delta_HP + m_stor*(1-delta_ch))
    T_ret_load_no_buffer = T_sup_load_no_buffer - Delta_T_load
    T_ret_HP_no_stor = (m_load*T_ret_load + m_buffer*T_B4*delta_bu) / (m_load + m_buffer*delta_bu)

    # ------------------------------------------------------
    # The functions to approximate
    # ------------------------------------------------------
    
    # Objective and constraints [OK]
    if   id == "Q_HP":          f = m_HP * cp * (T_sup_HP - T_ret_HP) * delta_HP
    elif id == "T_sup_load":    f = T_sup_load
    elif id == "m_buffer":      f = m_buffer
        
    # --- Buffer tank --- Top and Bottom [TEST]
    elif id == "Q_top_B1":      f = (2*delta_bu-1) * m_buffer * cp * (T_sup_load_no_buffer - T_B1)
    elif id == "Q_bottom_B4":   f = (2*delta_bu-1) * m_buffer * cp * (T_ret_load_no_buffer - T_B4)
    
    # --- Buffer tank --- Convection [CHECK]
    elif id == "Q_conv_B1":     f = -(2*delta_bu-1) * m_buffer * cp * (     - 1*T_B1 + T_B2)
    elif id == "Q_conv_B2":     f = -(2*delta_bu-1) * m_buffer * cp * (T_B1 - 2*T_B2 + T_B3)
    elif id == "Q_conv_B3":     f = -(2*delta_bu-1) * m_buffer * cp * (T_B2 - 2*T_B3 + T_B4)
    elif id == "Q_conv_B4":     f = -(2*delta_bu-1) * m_buffer * cp * (T_B3 - 1*T_B4)
    
    # --- Storage tanks --- Top and Bottom [TEST]
    elif id == "Q_top_S11":     f = (2*delta_ch-1) * m_stor * cp * (T_sup_HP - T_S11)
    elif id == "Q_top_S21":     f = (2*delta_ch-1) * m_stor * cp * (T_S14 - T_S21)
    elif id == "Q_top_S31":     f = (2*delta_ch-1) * m_stor * cp * (T_S24 - T_S31)
    elif id == "Q_bottom_S14":  f = (2*delta_ch-1) * m_stor * cp * (T_S21 - T_S14)
    elif id == "Q_bottom_S24":  f = (2*delta_ch-1) * m_stor * cp * (T_S31 - T_S24)
    elif id == "Q_bottom_S34":  f = (2*delta_ch-1) * m_stor * cp * (T_ret_HP_no_stor - T_S34)
    
    # --- Storage tanks --- Convection [CHECK]
    elif id == "Q_conv_S11":    f = -(2*delta_ch-1) * m_stor * cp * (      - 1*T_S11 + T_S12)
    elif id == "Q_conv_S12":    f = -(2*delta_ch-1) * m_stor * cp * (T_S11 - 2*T_S12 + T_S13)
    elif id == "Q_conv_S13":    f = -(2*delta_ch-1) * m_stor * cp * (T_S12 - 2*T_S13 + T_S14)
    elif id == "Q_conv_S14":    f = -(2*delta_ch-1) * m_stor * cp * (T_S13 - 1*T_S14)
    
    elif id == "Q_conv_S21":    f = -(2*delta_ch-1) * m_stor * cp * (      - 1*T_S21 + T_S22)
    elif id == "Q_conv_S22":    f = -(2*delta_ch-1) * m_stor * cp * (T_S21 - 2*T_S22 + T_S23)
    elif id == "Q_conv_S23":    f = -(2*delta_ch-1) * m_stor * cp * (T_S22 - 2*T_S23 + T_S24)
    elif id == "Q_conv_S24":    f = -(2*delta_ch-1) * m_stor * cp * (T_S23 - 1*T_S24)
    
    elif id == "Q_conv_S31":    f = -(2*delta_ch-1) * m_stor * cp * (      - 1*T_S31 + T_S32)
    elif id == "Q_conv_S32":    f = -(2*delta_ch-1) * m_stor * cp * (T_S31 - 2*T_S32 + T_S33)
    elif id == "Q_conv_S33":    f = -(2*delta_ch-1) * m_stor * cp * (T_S32 - 2*T_S33 + T_S34)
    elif id == "Q_conv_S34":    f = -(2*delta_ch-1) * m_stor * cp * (T_S33 - 1*T_S34)
    
    else: raise ValueError("\nThe function ID '{}' does not exist.".format(id))
    
    # ------------------------------------------------------
    # First order Taylor expansion of f around "a"
    # ------------------------------------------------------

    # Compute the gradient
    grad_f = [diff(f,var_i) for var_i in all_variables]
    
    # Evaluate f and its gradient at "a"
    try:
        f_a = float(f.subs(a))
        grad_f_a = [round(float(grad_f_i.subs(a)),5) for grad_f_i in grad_f]
    except:
        raise ValueError(f"Function f={id} is not defined at 'a' (f(a) and/or grad_f(a) are not floats).")
        
    # Check for NaN values in f and its gradient at "a"
    if math.isnan(f_a):
        raise ValueError(f"Function f={id} is not defined at 'a' (f(a) is NaN).")
    for grad_f_a_i in grad_f_a:
        if math.isnan(grad_f_a_i):
            raise ValueError(f"Function f={id} is not defined at 'a' (grad_f(a) contains a NaN).")
    
    # f_approx(x) = f(a) + grad_f(a).(x-a)
    f_approx = f_a
    for i in range(len(grad_f_a)):
        f_approx += grad_f_a[i] * (all_variables[i] - a[all_variables[i]])
        
    # This is useful for prints, much easier to read
    approx_readable = f_approx
                
    # If y is not real, we just want a symbolic expression
    if not real:
        f_approx = float(f_a)
        for i in range(len(grad_f_a)):
            f_approx += float(grad_f_a[i]) * (y[i] - float(a[all_variables[i]]))
    
    # ------------------------------------------------------
    # Return f_id(y), f_id_approx(y) and the relative error
    # ------------------------------------------------------
    
    # If y is real, we can evaluate the function at that point
    if real:
        exact = f.subs(y)
        approx = f_approx.subs(y)
        rel_error = np.abs((f.subs(y)-f_approx.subs(y))/f.subs(y))*100
        
    # If not, we return the function itself
    else:
        exact = f
        approx = f_approx
        rel_error = np.nan
        
    return {'exact': exact, 'approx': approx, 'approx_readable': approx_readable, 'rel_error': rel_error, }
