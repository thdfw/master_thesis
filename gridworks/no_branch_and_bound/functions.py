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
m_buffer = (m_HP * delta_HP - m_stor * (2*delta_ch-1) - m_load) / (2 * delta_bu - 1)

# Temperatures entering and exiting the load
T_sup_load = (m_HP*T_sup_HP*delta_HP + m_stor*T_S11*(1-delta_ch) + m_buffer*T_B1*(1-delta_bu)) / (m_HP*delta_HP + m_stor*(1-delta_ch) + m_buffer*(1-delta_bu))
T_ret_load = T_sup_load - Delta_T_load

# Temperature entering the heat pump
T_ret_HP = (m_load*T_ret_load + m_stor*T_S34*delta_ch + m_buffer*T_B4*delta_bu) / (m_load + m_stor*delta_ch + m_buffer*delta_bu)

# Intermediate temperatures
T_HP_stor = (m_HP*T_sup_HP*delta_HP + m_stor*T_S11*(1-delta_ch)) / (m_HP*delta_HP + m_stor*(1-delta_ch))
T_ret_load_buffer = (m_load*T_ret_load + m_buffer*T_B4*delta_bu) / (m_load + m_buffer*delta_bu)

# ------------------------------------------------------
# The functions to approximate
# ------------------------------------------------------

functions = {
    # Objective and constraints [ok]
    "Q_HP":         m_HP * cp * (T_sup_HP - T_ret_HP) * delta_HP,
    "T_sup_load":   T_sup_load,
    "m_buffer":     m_buffer,
        
    # --- Buffer tank --- Convection [ok]
    "Q_conv_B1":    m_buffer * cp * (T_B2 - T_B1),
    "Q_conv_B2":    m_buffer * cp * (T_B1 - 2*T_B2 + T_B3),
    "Q_conv_B3":    m_buffer * cp * (T_B2 - 2*T_B3 + T_B4),
    "Q_conv_B4":    m_buffer * cp * (T_B3 - T_B4),
    
    # --- Buffer tank --- Top and Bottom [ok]
    "Q_top_B":     delta_bu     * m_buffer * cp * (T_HP_stor - T_B1),
    "Q_bottom_B":  (1-delta_bu) * m_buffer * cp * (T_ret_load - T_B4),
    
    # --- Storage taks --- Convection [ok]
    "Q_conv_S11":   m_stor * cp * (T_S12 - T_S11),
    "Q_conv_S12":   m_stor * cp * (T_S11 - 2*T_S12 + T_S13),
    "Q_conv_S13":   m_stor * cp * (T_S12 - 2*T_S13 + T_S14),
    "Q_conv_S14":   m_stor * cp * (T_S13 - T_S14),
    
    "Q_conv_S21":   m_stor * cp * (T_S22 - T_S21),
    "Q_conv_S22":   m_stor * cp * (T_S21 - 2*T_S22 + T_S23),
    "Q_conv_S23":   m_stor * cp * (T_S22 - 2*T_S23 + T_S24),
    "Q_conv_S24":   m_stor * cp * (T_S23 - T_S24),
    
    "Q_conv_S31":   m_stor * cp * (T_S32 - T_S31),
    "Q_conv_S32":   m_stor * cp * (T_S31 - 2*T_S32 + T_S33),
    "Q_conv_S33":   m_stor * cp * (T_S32 - 2*T_S33 + T_S34),
    "Q_conv_S34":   m_stor * cp * (T_S33 - T_S34),

    # --- Storage tanks --- Top and Bottom [ok]
    "Q_top_S1":    delta_ch * m_stor * cp * (T_sup_HP - T_S11),
    "Q_top_S2":    delta_ch * m_stor * cp * (T_S14 - T_S21),
    "Q_top_S3":    delta_ch * m_stor * cp * (T_S24 - T_S31),
    "Q_bottom_S1": (1-delta_ch) * m_stor * cp * (T_S21 - T_S14),
    "Q_bottom_S2": (1-delta_ch) * m_stor * cp * (T_S31 - T_S24),
    "Q_bottom_S3": (1-delta_ch) * m_stor * cp * (T_ret_load_buffer - T_S34),
}

# ------------------------------------------------------
# Compute the gradients of the functions to approximate
# ------------------------------------------------------

gradients = {id: [diff(f,var_i) for var_i in all_variables] for id, f in functions.items()}

# ------------------------------------------------------
# In the case exact value with symbolic values
# ------------------------------------------------------
'''
In the particular case where we ask for the exact functions with
u and x terms that are casadi symbolic terms, need to redefine the functions
replacing the variable names by u and x.
'''
def functions_exact_sym(id,u,x):

    # Mass flow rate at buffer tank
    m_buffer = (m_HP * u[4] - u[1] * (2*u[2]-1) - m_load) / (2 * u[3] - 1)

    # Temperatures entering and exiting the load
    T_sup_load = (m_HP*u[0]*u[4] + u[1]*x[4]*(1-u[2]) + m_buffer*x[0]*(1-u[3])) / (m_HP*u[4] + u[1]*(1-u[2]) + m_buffer*(1-u[3]))
    T_ret_load = T_sup_load - Delta_T_load

    # Temperature entering the heat pump
    T_ret_HP = (m_load*T_ret_load + u[1]*x[15]*u[2] + m_buffer*x[3]*u[3]) / (m_load + u[1]*u[2] + m_buffer*u[3])

    # Intermediate temperatures
    T_HP_stor = (m_HP*u[0]*u[4] + u[1]*x[4]*(1-u[2])) / (m_HP*u[4] + u[1]*(1-u[2]))
    T_ret_load_buffer = (m_load*T_ret_load + m_buffer*x[3]*u[3]) / (m_load + m_buffer*u[3])

    # ------------------------------------------------------
    # The functions to approximate
    # ------------------------------------------------------

    functions = {
        # Objective and constraints [ok]
        "Q_HP":         m_HP * cp * (u[0] - T_ret_HP) * u[4],
        "T_sup_load":   T_sup_load,
        "m_buffer":     m_buffer,
            
        # --- Buffer tank --- Convection [ok]
        "Q_conv_B1":    m_buffer * cp * (x[1] - x[0]),
        "Q_conv_B2":    m_buffer * cp * (x[0] - 2*x[1] + x[2]),
        "Q_conv_B3":    m_buffer * cp * (x[1] - 2*x[2] + x[3]),
        "Q_conv_B4":    m_buffer * cp * (x[2] - x[3]),
        
        # --- Buffer tank --- Top and Bottom [ok]
        "Q_top_B":     u[3]     * m_buffer * cp * (T_HP_stor - x[0]),
        "Q_bottom_B":  (1-u[3]) * m_buffer * cp * (T_ret_load - x[3]),
        
        # --- Storage taks --- Convection [ok]
        "Q_conv_S11":   u[1] * cp * (x[5] - x[4]),
        "Q_conv_S12":   u[1] * cp * (x[4] - 2*x[5] + x[6]),
        "Q_conv_S13":   u[1] * cp * (x[5] - 2*x[6] + x[7]),
        "Q_conv_S14":   u[1] * cp * (x[6] - x[7]),
        
        "Q_conv_S21":   u[1] * cp * (x[9] - x[8]),
        "Q_conv_S22":   u[1] * cp * (x[8] - 2*x[9] + x[10]),
        "Q_conv_S23":   u[1] * cp * (x[9] - 2*x[10] + x[11]),
        "Q_conv_S24":   u[1] * cp * (x[10] - x[11]),
        
        "Q_conv_S31":   u[1] * cp * (x[13] - x[12]),
        "Q_conv_S32":   u[1] * cp * (x[12] - 2*x[13] + x[14]),
        "Q_conv_S33":   u[1] * cp * (x[13] - 2*x[14] + x[15]),
        "Q_conv_S34":   u[1] * cp * (x[14] - x[15]),

        # --- Storage tanks --- Top and Bottom [ok]
        "Q_top_S1":    u[2] * u[1] * cp * (u[0] - x[4]),
        "Q_top_S2":    u[2] * u[1] * cp * (x[7] - x[8]),
        "Q_top_S3":    u[2] * u[1] * cp * (x[11] - x[12]),
        "Q_bottom_S1": (1-u[2]) * u[1] * cp * (x[8] - x[7]),
        "Q_bottom_S2": (1-u[2]) * u[1] * cp * (x[12] - x[11]),
        "Q_bottom_S3": (1-u[2]) * u[1] * cp * (T_ret_load_buffer - x[15]),
    }
    
    return functions[id]

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
    values:   the point around which we linearize the function
    f_a:      dict with f(a) for every f
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

        if real:
            # Get the function by ID and evaluate at y=[u,x]
            f = functions[id]
            y = {variable: value_y for variable, value_y in zip(all_variables,(u+x))}
            return float(f.subs(y))
        
        else:
            # Redefine the function using u and x
            f = functions_exact_sym(id, u, x)
            return f
    
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
    f_approx_print = f_a
    for i in range(len(grad_f_a)):
        f_approx += float(grad_f_a[i]) * (y[i] - float(values_a[i]))
        f_approx_print += grad_f_a[i] * (all_variables[i] - values_a[i])

    #print(f"{id} = {f_approx_print}\n")
               
    return f_approx
