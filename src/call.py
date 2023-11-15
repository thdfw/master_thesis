from linear_approx import f_id_y
import casadi
from sympy import symbols, diff, Symbol
import numpy as np
import matplotlib.pyplot as plt

# Which function do you want?
id = 2

# Define the point a around which to linearize
a_u = [310,  0.25,   0,    1,    0,    0]
a_x = [308]*4 + [313]*12

# ---------------------------------------------
# ---- Sample case 1: We ask for a real y -----
# ---------------------------------------------
#      T_HP, m_stor, d_ch, d_bu, d_HP, d_R

y_u = [320,  0.25,   0,    1,    1,    0]
y_x = [308]*4 + [313]*12

f = f_id_y(id=id, a_u=a_u, a_x=a_x, y_u=y_u, y_x=y_x, real=True)
approx = f['approx']
exact = f['exact']
error = f['rel_error']

print("\n----------------------")
print("y = {}".format([y_u, y_x]))
print("a = {}".format([a_u, a_x]))
print("\nEstimated f_{}(y): {}".format(id,round(approx)))
print("True f_{}(y): {}".format(id,round(exact)))
print("Error of estimation: {}%".format(round(error)))

# -------------------------------------------------
# ---- Sample case 2: We ask for a symbolic y -----
# -------------------------------------------------

opti = casadi.Opti()
x = opti.variable(16, 10+1)  # T_B1,...,T_B4, T_S11,...,TS34
u = opti.variable(6, 10)     # T_sup_HP m_stor delta_HP delta_ch delta_dch delta_R
y_u1 = u[:,0]
y_x1 = x[:,0]

# Estimate f_id(x) at y=(y_u,y_x) with linearization around a=(a_u,a_x)

f = f_id_y(id=id, a_u=a_u, a_x=a_x, y_u=y_u1, y_x=y_x1, real=False)
approx = f['approx']
exact = f['exact']
error = f['rel_error']

print("\n----------------------")
print("y = {}".format([y_u1, y_x1]))
print("a = {}".format([a_u, a_x]))
print("\nEstimated f_{}(y): {}\n".format(id,approx))
