from sympy import symbols, diff
import numpy as np
import casadi
import math

# ------------------------------------------------------
# Variables and constants
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
T_sup_load_no_buffer = (m_HP*T_sup_HP*delta_HP + m_stor*T_S11*(1-delta_ch)) / (m_HP*delta_HP + m_stor*(1-delta_ch))
T_ret_load_no_buffer = T_sup_load_no_buffer - Delta_T_load
T_ret_HP_no_stor = (m_load*T_ret_load + m_buffer*T_B4*delta_bu) / (m_load + m_buffer*delta_bu)

# ------------------------------------------------------
# The functions to approximate
# ------------------------------------------------------

functions = {
    # Objective and constraints [OK]
    "Q_HP":         m_HP * cp * (T_sup_HP - T_ret_HP) * delta_HP,
    "T_sup_load":   T_sup_load,
    "m_buffer":     m_buffer,
        
    # --- Buffer tank --- Top and Bottom [TEST]
    "Q_top_B1":     (2*delta_bu-1) * m_buffer * cp * (T_sup_load_no_buffer - T_B1),
    "Q_bottom_B4":  (2*delta_bu-1) * m_buffer * cp * (T_ret_load_no_buffer - T_B4),

    # --- Buffer tank --- Convection [CHECK]
    "Q_conv_B1":    -(2*delta_bu-1) * m_buffer * cp * (     - 1*T_B1 + T_B2),
    "Q_conv_B2":    -(2*delta_bu-1) * m_buffer * cp * (T_B1 - 2*T_B2 + T_B3),
    "Q_conv_B3":    -(2*delta_bu-1) * m_buffer * cp * (T_B2 - 2*T_B3 + T_B4),
    "Q_conv_B4":    -(2*delta_bu-1) * m_buffer * cp * (T_B3 - 1*T_B4),

    # --- Storage tanks --- Top and Bottom [TEST]
    "Q_top_S11":    (2*delta_ch-1) * m_stor * cp * (T_sup_HP - T_S11),
    "Q_top_S21":    (2*delta_ch-1) * m_stor * cp * (T_S14 - T_S21),
    "Q_top_S31":    (2*delta_ch-1) * m_stor * cp * (T_S24 - T_S31),
    "Q_bottom_S14": (2*delta_ch-1) * m_stor * cp * (T_S21 - T_S14),
    "Q_bottom_S24": (2*delta_ch-1) * m_stor * cp * (T_S31 - T_S24),
    "Q_bottom_S34": (2*delta_ch-1) * m_stor * cp * (T_ret_HP_no_stor - T_S34),
    
    # --- Storage taks --- Convection [CHECK]
    "Q_conv_S11":   -(2*delta_ch-1) * m_stor * cp * (      - 1*T_S11 + T_S12),
    "Q_conv_S12":   -(2*delta_ch-1) * m_stor * cp * (T_S11 - 2*T_S12 + T_S13),
    "Q_conv_S13":   -(2*delta_ch-1) * m_stor * cp * (T_S12 - 2*T_S13 + T_S14),
    "Q_conv_S14":   -(2*delta_ch-1) * m_stor * cp * (T_S13 - 1*T_S14),
    "Q_conv_S21":   -(2*delta_ch-1) * m_stor * cp * (      - 1*T_S21 + T_S22),
    "Q_conv_S22":   -(2*delta_ch-1) * m_stor * cp * (T_S21 - 2*T_S22 + T_S23),
    "Q_conv_S23":   -(2*delta_ch-1) * m_stor * cp * (T_S22 - 2*T_S23 + T_S24),
    "Q_conv_S24":   -(2*delta_ch-1) * m_stor * cp * (T_S23 - 1*T_S24),
    "Q_conv_S31":   -(2*delta_ch-1) * m_stor * cp * (      - 1*T_S31 + T_S32),
    "Q_conv_S32":   -(2*delta_ch-1) * m_stor * cp * (T_S31 - 2*T_S32 + T_S33),
    "Q_conv_S33":   -(2*delta_ch-1) * m_stor * cp * (T_S32 - 2*T_S33 + T_S34),
    "Q_conv_S34":   -(2*delta_ch-1) * m_stor * cp * (T_S33 - 1*T_S34)
}

# Compute all the gradients
gradients = {id: [diff(f,var_i) for var_i in all_variables] for id, f in functions.items()}

# ------------------------------------------------------
# Get f(a) and grad_f(a) for all functions
# ------------------------------------------------------

'''
Input: the point "a" around which to linearize
Output: f(a) for all non linear functions defined in this file
'''
# Compute all the functions at point "a"
def get_all_f(a):
    
    a = {variable: value_a for variable, value_a in zip(all_variables,a)}
    functions_a = {id: f.subs(a) for id, f in functions.items()}
    
    # Check that all f(a) are valid
    for id, f_a in functions_a.items():
        try:
            f_a = float(f_a)
            if math.isnan(f_a):
                raise ValueError(f"Function f={id} is not defined at 'a' (f(a) is NaN).")
        except:
            raise ValueError(f"Function f={id} is not defined at 'a' (f(a) is not a float).")
            
    return functions_a

'''
Input: the point "a" around which to linearize
Output: grad_f(a) for all non linear functions defined in this file
'''
# Compute all the gradients at point "a"
def get_all_grad_f(a):
    
    a = {variable: value_a for variable, value_a in zip(all_variables,a)}
    gradients_a = {id: [grad_f_i.subs(a) for grad_f_i in grad_f] for id, grad_f in gradients.items()}
    
    # Check that all grad_f(a) are valid
    for id, grad_f_a in gradients_a.items():
        try:
            for grad_f_a_i in grad_f_a:
                grad_f_a_i = float(grad_f_a_i)
                if math.isnan(grad_f_a_i):
                    raise ValueError(f"Function f={id} is not defined at 'a' (grad_f(a) contains a NaN).")
        except:
            raise ValueError(f"Function f={id} is not defined at 'a' (grad_f(a) is not a list of floats).")
    
    return gradients_a

# ------------------------------------------------------
# Get f(y) or f_a(y)
# ------------------------------------------------------

'''
GOAL:
Get the first order Taylor expansion (linear approximation) of a function f around a point "a"
Evaluate the value of the function and the approximation at a point "y"

INPUTS:
- id: The function we want (e.g. id='m_buffer')
- u: the input variables
- x: the state variables
- a is a dict
    values: the point around which we linearize the function
    f_a: dict with f(a) for every f
    grad_f_a: dict with grad_f(a) for every f
- real: True if y is real, False if y is symbolic (casadi terms)
- approx: True if we want f_a(y), False if we want f(y)

OUTPUTS:
- f(y) or f_a(y)
'''
def get_function(id, u, x, a, real, approx):
        
    # ------------------------------------------------------
    # Case 1: Want exact value of the function
    # ------------------------------------------------------
    
    if not approx:

        # Get the desired function by the provided id
        f = functions[id]
    
        # Construct "y" from given vectors y = [u, x]
        y = {variable: value_y for variable, value_y in zip(all_variables,(u+x))}
        
        if not real:
            ValueError("Symbolic + exact scenario has not been implemented yet.")
        
        return float(f.subs(y)) if real else f
    
    # ------------------------------------------------------
    # Case 2: Want linear approximation around "a"
    # ------------------------------------------------------
    
    # Get the desired function by the provided id
    values_a = a['values']
    f_a      = a['functions_a'][id]
    grad_f_a = a['gradients_a'][id]
    
    # Construct "y" from given vectors y = [u, x]
    y = (u+x) if real else casadi.vertcat(u,x)
    
    # f_a(y) = f(a) + grad_f(a).(y-a)
    f_approx = float(f_a)
    for i in range(len(grad_f_a)):
        f_approx += float(grad_f_a[i]) * (y[i] - float(values_a[i]))
               
    return f_approx
    
    
    '''
    # The best for prints
    if real:
        y = {variable: value_y for variable, value_y in zip(all_variables,(u+x))}
        f_approx = float(f_a)
        f_approx += grad_f_a[i] * (all_variables[i] - a[all_variables[i]]) # where a[] needs to be defined as a dict like y
        return f_approx.subs(y)
    '''
