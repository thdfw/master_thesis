from sympy import symbols, diff
import numpy as np
import casadi
import math

# Choose between solving the general case or a given combination of the deltas
general = False

if general:
    # Solve the general case
    case = {'d_ch': delta_ch, 'd_bu': delta_bu, 'd_HP': delta_HP, 'd_R': delta_R}
else:
    # Choose a specific combination of the binary variables
    case = {'d_ch': 0, 'd_bu': 1, 'd_HP': 0, 'd_R':0}


# ------------------------------------------------------
# Define all variables and constants
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
Delta_T_load = 5/9*20
cp = 4187

# Mass flow rate from HP
B_0M, B_1M = 0.5, 0 #4.2669, -0.0117


# ------------------------------------------------------
# Define all functions
# ------------------------------------------------------

def get_all_f(case):

    # Unpack the specific case
    delta_ch = case['d_ch']
    delta_bu = case['d_bu']
    delta_HP = case['d_HP']
    delta_R  = case['d_R']
    
    # Mass flow rate from HP
    m_HP = B_0M + B_1M * T_sup_HP

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
        
        "T_sup_load": T_sup_load,
        "T_ret_HP": T_ret_HP,
        "m_HP": m_HP,
    }

    # Compute the gradients of the functions to approximate
    gradients = {id: [diff(f,var_i) for var_i in all_variables] for id, f in functions.items()}
    
    return functions, gradients


# ------------------------------------------------------
# Compute all functions and gradients
# ------------------------------------------------------

functions, gradients = get_all_f(case)


# ------------------------------------------------------
# Functions for the non linearized problem
# ------------------------------------------------------
'''
In the functions defined above, the variables are SymPy symbols.
These symbols can not be replaced by CasADi variables.

However, when we want to compute a non linearized version of the problem,
we need these functions to be expressed using CasADi variables.

In that case, we call the following function.
'''
def functions_exact_sym(id, u, x):

    # Get the delta terms
    delta_ch = u[2] if general else case['d_ch']
    delta_bu = u[3] if general else case['d_bu']
    delta_HP = u[4] if general else case['d_HP']
    delta_R  = u[5] if general else case['d_R']

    # Get the other variables from the inputs and states
    T_sup_HP, m_stor = u[0], u[1]
    T_B1, T_B2, T_B3, T_B4 = x[0], x[1], x[2], x[3]
    T_S11, T_S12, T_S13, T_S14 = x[4], x[5], x[6], x[7]
    T_S21, T_S22, T_S23, T_S24 = x[8], x[9], x[10], x[11]
    T_S31, T_S32, T_S33, T_S34 = x[12], x[13], x[14], x[15]
    
    # Mass flow rate from HP
    m_HP = B_0M + B_1M * T_sup_HP
    
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

    # The functions to approximate
    functions_sym = {
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
        
        "T_sup_load": T_sup_load,
        "T_ret_HP": T_ret_HP,
        "m_HP": m_HP,
    }
    
    return functions_sym[id]
    
    
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
Evaluate any function f at a point "y": f(y)
Evaluate the linearization of any f around "a" at point "y": f_a(y)

INPUTS:
- id: The function we want to evaluate (e.g. id='m_buffer')
- u: the input variables
- x: the state variables
- a is a dict
    values:   the point around which we linearize the function
    f_a:      dict with f(a) for every f
    grad_f_a: dict with grad_f(a) for every f
- real: True if y is real (numeric), False if y is symbolic (casadi terms)
- approx: True if we want f_a(y), False if we want f(y)

OUTPUTS:
- f(y) or f_a(y)
'''
def get_function(id, u, x, a, real, approx):
        
    # ------------------------------------------------------
    # Case 1: Want exact value of the function: f(y)
    # ------------------------------------------------------
    
    if not approx:

        if real:
            # Get the function by ID and evaluate at y=[u,x]
            f = functions[id]
            y = {variable: value_y for variable, value_y in zip(all_variables,(u+x))}
            return float(f.subs(y))
        
        else:
            # Get the function by ID and return it with CasADi terms
            f = functions_exact_sym(id, u, x)
            return f
    
    # ------------------------------------------------------
    # Case 2: Want linear approximation around "a": f_a(y)
    # ------------------------------------------------------
    
    # Get the desired function by the provided id
    values_a = a['values']
    f_a      = a['functions_a'][id]
    grad_f_a = a['gradients_a'][id]
    
    # Construct "y" from given vectors y = [u, x]
    y = (u+x) if real else casadi.vertcat(u,x)
    
    # Get f_a(y) = f(a) + grad_f(a).(y-a)
    f_approx = float(f_a)
    f_approx_print = f_a
    for i in range(len(grad_f_a)):
        f_approx += float(grad_f_a[i]) * (y[i] - float(values_a[i]))
        f_approx_print += grad_f_a[i] * (all_variables[i] - values_a[i])

    # print(f"{id} = {f_approx_print}\n")
    return f_approx
