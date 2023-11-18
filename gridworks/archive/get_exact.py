from sympy import symbols, diff
import numpy as np
import casadi
from linear_approx import f_approx

# Tanks
A = 0.25 #m2
z = 0.24 #m
rho = 997 #kg/m3
m_layer = rho*A*z #kg
T_w_min = 273 + 10 #K
T_w_max = 273 + 80 #K

# Other
delta_t_s = 300 #seconds
cp = 4187 #J/kgK

'''
INPUTS:
u_0: optimal input at time step 0
x_0: state at time step 0

OUTPUTS:
The state obtained by implementing u_0 at x_0: x_1 = f(x_0,u_0)
'''

def x_1(u_0, x_0):

    a_u, a_x = [0]*6, [0]*16
    y_u, y_x = u_0, x_0

    # All heat transfers are 0 unless specified otherwise later
    Q_top_B = Q_bottom_B = Q_conv_B = Q_losses_B = [0]*4
    Q_top_S = Q_bottom_S = Q_conv_S = Q_losses_S = Q_R_S = [0]*12
    
    # For the buffer tank B
    Q_top_B[0]      = f_approx(id="Q_top_B1", a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    Q_bottom_B[3]   = f_approx(id="Q_bottom_B4", a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    for i in range(1,5):
        Q_conv_B[i-1] = f_approx(id="Q_conv_B{}".format(i), a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    
    # For the storage tank S
    Q_top_S[0]      = f_approx(id="Q_top_S11", a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    Q_top_S[4]      = f_approx(id="Q_top_S21", a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    Q_top_S[8]      = f_approx(id="Q_top_S31", a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    Q_bottom_S[3]   = f_approx(id="Q_bottom_S14", a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    Q_bottom_S[7]   = f_approx(id="Q_bottom_S24", a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    Q_bottom_S[11]  = f_approx(id="Q_bottom_S34", a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']
    for i in range(1,4):
        for j in range(1,5):
            Q_conv_S[4*(i-1)+(j-1)] = f_approx(id="Q_conv_S{}{}".format(i,j), a_u=a_u, a_x=a_x, y_u=u_0, y_x=x_0, real=True)['exact']

    # Next state for buffer and storage
    const = delta_t_s / (m_layer * cp)
    x_plus_B = [x_0[i] + const * (Q_top_B[i] + Q_bottom_B[i] + Q_conv_B[i] - Q_losses_B[i]) for i in range(4)]
    x_plus_S = [x_0[i] + const * (Q_top_S[i] + Q_bottom_S[i] + Q_conv_S[i] - Q_losses_S[i] + Q_R_S[i]) for i in range(12)]

    # Bring everything together
    x_plus = []
    for i in range(len(x_plus_B)): x_plus.append(x_plus_B[i])
    for i in range(len(x_plus_S)): x_plus.append(x_plus_S[i])
    
    return [round(float(x),2) for x in x_plus]   
