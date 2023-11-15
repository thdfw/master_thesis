from sympy import symbols, diff
import numpy as np
import casadi

'''
GOAL:
Get the first order Taylor expansion (linear approximation) of a function f_i around a point "a"
Evaluate the value of the function and the approximation at a point "y"

INPUTS:
- id: The function number we want (e.g. id=2 if we want the function f_2)
- a = [a_u, a_x] is the point around which we linearize the function
    a_u is the component for the inputs "u"
    a_x is the component for the states "x"
- y = [y_u, y_x] is the point at which we want to get the function value
    y_u is the component for the inputs "u"
    y_x is the component for the states "x"
- real: True if y is real, False if y is symbolic (casadi terms)

OUTPUTS:
Returns a dictionnary with:
- Exact: f_id(y)
- Approx: f_id_approx(y)
- Rel_error: the relative error of the approximation
'''

def f_id_y(id, a_u, a_x, y_u, y_x, real):

    # ------------------------------------------------------
    # Define variables and construct vectors
    # ------------------------------------------------------

    # Define all variables as symbols
    T_sup_HP, m_stor = symbols('T_sup_HP m_stor')
    delta_ch, delta_bu, delta_HP = symbols('delta_ch delta_bu delta_hp')
    T_B1, T_B2, T_B3, T_B4 = symbols('T_B1 T_B2 T_B3 T_B4')
    T_S11, T_S12, T_S13, T_S14, T_S21, T_S22, T_S23, T_S24, T_S31, T_S32, T_S33, T_S34 \
    = symbols('T_S11 T_S12 T_S13 T_S14 T_S21 T_S22 T_S23 T_S24 T_S31 T_S32 T_S33 T_S34')
    
    # Gather all the symbols in a list
    all_variables = [T_sup_HP, m_stor, delta_ch, delta_bu, delta_HP, T_B1, T_B2, T_B3, T_B4, T_S11, T_S12, T_S13, T_S14, T_S21, T_S22, T_S23, T_S24, T_S31, T_S32, T_S33, T_S34]
    
    # Construct "a" from given data
    a = {T_sup_HP: a_u[0], m_stor: a_u[1], delta_ch: a_u[2], delta_bu: a_u[3], delta_HP: a_u[4],
    T_B1:  a_x[0],  T_B2:  a_x[1],  T_B3:  a_x[2],  T_B4:  a_x[3],
    T_S11: a_x[4],  T_S12: a_x[5],  T_S13: a_x[6],  T_S14: a_x[7],
    T_S21: a_x[8],  T_S22: a_x[9],  T_S23: a_x[10], T_S24: a_x[11],
    T_S31: a_x[12], T_S32: a_x[13], T_S33: a_x[14], T_S34: a_x[15]}

    # Construct "y" from given data
    if real:
        y = {T_sup_HP: y_u[0], m_stor: y_u[1], delta_ch: y_u[2], delta_bu: y_u[3], delta_HP: y_u[4],
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
    c_p = 4187

    # ------------------------------------------------------
    # Useful functions
    # ------------------------------------------------------

    # Mass flow rate at buffer tank
    m_buffer = (m_HP * delta_HP - m_stor * (2 * delta_ch - 1) - m_load) / (2 * delta_bu - 1)
    
    # Mixing temperatures
    T_sup_load = (m_HP*T_sup_HP*delta_HP + m_stor*T_S11*(1-delta_ch) + m_buffer*T_B1*(1-delta_bu)) / (m_HP*delta_HP + m_stor*(1-delta_ch) + m_buffer*(1-delta_bu))
    T_ret_load = T_sup_load - Delta_T_load
    T_ret_HP = (m_load*T_ret_load + m_stor*T_S34*delta_ch + m_buffer*T_B4*delta_bu) / (m_load + m_stor*delta_ch + m_buffer*delta_bu)

    # ------------------------------------------------------
    # The functions to approximate
    # ------------------------------------------------------

    # f1
    if id == 1: f = T_ret_load * delta_ch

    # f2
    if id == 2: f = T_sup_load

    # f3,...,f6
    if id == 3: f = (m_HP * delta_HP - m_stor * (2 * delta_ch - 1) - m_load) * c_p * T_B1
    if id == 4: f = (m_HP * delta_HP - m_stor * (2 * delta_ch - 1) - m_load) * c_p * T_B2
    if id == 5: f = (m_HP * delta_HP - m_stor * (2 * delta_ch - 1) - m_load) * c_p * T_B3
    if id == 6: f = (m_HP * delta_HP - m_stor * (2 * delta_ch - 1) - m_load) * c_p * T_B4

    # f7, f8
    if id == 7: f = (m_HP * delta_HP - m_stor * (2 * delta_ch - 1) - m_load) * c_p * T_sup_load
    if id == 8: f = (m_HP * delta_HP - m_stor * (2 * delta_ch - 1) - m_load) * c_p * T_ret_load

    # f9,...,f20
    if id == 9: f = (2*delta_ch-1) * m_stor * c_p * T_S11
    if id == 10: f = (2*delta_ch-1) * m_stor * c_p * T_S12
    if id == 11: f = (2*delta_ch-1) * m_stor * c_p * T_S13
    if id == 12: f = (2*delta_ch-1) * m_stor * c_p * T_S14
    if id == 13: f = (2*delta_ch-1) * m_stor * c_p * T_S21
    if id == 14: f = (2*delta_ch-1) * m_stor * c_p * T_S22
    if id == 15: f = (2*delta_ch-1) * m_stor * c_p * T_S23
    if id == 16: f = (2*delta_ch-1) * m_stor * c_p * T_S24
    if id == 17: f = (2*delta_ch-1) * m_stor * c_p * T_S31
    if id == 18: f = (2*delta_ch-1) * m_stor * c_p * T_S32
    if id == 19: f = (2*delta_ch-1) * m_stor * c_p * T_S33
    if id == 20: f = (2*delta_ch-1) * m_stor * c_p * T_S34

    # f21, f22
    if id == 21: f = (2*delta_ch-1) * m_stor * c_p * T_sup_HP
    if id == 22: f = (2*delta_ch-1) * m_stor * c_p * T_ret_HP

    # ------------------------------------------------------
    # First order Taylor expansion of f around "a"
    # ------------------------------------------------------

    # Compute the gradient
    grad_f = [diff(f,var_i) for var_i in all_variables]
    
    # Evaluate f and its gradient at "a"
    f_a = f.subs(a)
    grad_f_a = [round(grad_f_i.subs(a),3) for grad_f_i in grad_f]

    # f_approx(x) = f(a) + grad_f(a).(x-a)
    if real:
        f_approx = f_a
        for i in range(len(grad_f_a)):
            f_approx += grad_f_a[i] * (all_variables[i] - a[all_variables[i]])
            
    else:
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
        
    return {'exact': exact, 'approx': approx, 'rel_error': rel_error, 'f_a': f_a, 'grad_f_a': grad_f_a}
