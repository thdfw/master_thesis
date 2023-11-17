import casadi
import numpy as np
import matplotlib.pyplot as plt
from linear_approx import f_approx
import get_exact

# ------------------------------------------------------
# Select problem type and solver
# ------------------------------------------------------

LINEAR  = True  # Linearized or Non-Linear
MIP     = True  # Mixed-integer or continuous
GUROBI  = True  # Gurobi or Ipopt

# ------------------------------------------------------
# Constants
# ------------------------------------------------------

# Heat pump
Q_HP_min = 8000 #W
Q_HP_max = 14000 #W

# Load
T_sup_load_min = 273 + 38 #K

# Tanks
A = 0.25 #m2
z = 0.24 #m
rho = 997 #kg/m3
m_layer = rho*A*z #kg
T_w_min = 273 + 10 #K
T_w_max = 273 + 80 #K

# Other
cp = 4187 #J/kgK

# ------------------------------------------------------
# Variables
# ------------------------------------------------------

# Horizon x = x_0,...,x_N
N = 3

# Time step
delta_t_m = 5
delta_t_s = delta_t_m*60
delta_t_h = delta_t_m/60

# Simulation time
num_iterations = 3

# Initialize CasADi
if GUROBI:  opti = casadi.Opti('conic')
else:       opti = casadi.Opti()

# Define state and input variables
u = opti.variable(6, N)     # T_sup_HP, m_stor, d_ch, d_bu, d_HP, d_R
x = opti.variable(16, N+1)  # T_B1,...,T_B4, T_S11,...,T_S14, T_S21,...,T_S24, T_S31,...,T_S34

# All variables are continuous except d_ch, d_bu and d_HP (binary)
discrete_var = ([0]*2 + [1]*3 + [0]) * N
discrete_var += [0]*16 * (N+1)

# ------------------------------------------------------
# Problem type and solver
# ------------------------------------------------------

if GUROBI:
    if MIP:
        print("\nSolver: Gurobi \nVariables: Mixed-Integer")
        solver_opts = {'discrete': discrete_var, 'gurobi.OutputFlag': 0}
    else:
        print("\nSolver: Gurobi \nVariables: Continuous\n")
        solver_opts = {'gurobi.OutputFlag': 0}
else:
    print("\nSolver: Ipopt \nVariables: Continuous")
    solver_opts = {'ipopt.print_level': 0, 'print_time': 0, 'ipopt.tol': 1e-4}
    
if LINEAR:
    print("Problem type: Linearized\n")
    print("Computing linear approximations...")
    exact_or_approx = 'approx'
else:
    print("Problem type: Non-linear\n")
    exact_or_approx = 'exact'
    
# ------------------------------------------------------
# Parameters
# ------------------------------------------------------

x_0 = opti.parameter(16)
c_el = opti.parameter(N)

# Get all electricity prices
c_el_all = [12] + [2] + [55] + [18.97]*12 + [18.92]*3 + [11]*9 + [18.21]*12 + [16.58]*12 + [16.27]*12 + [15.49]*12 + [14.64]*12 + [18.93]*12 + [45.56]*12 + [26.42]*12 + [18.0]*12 + [17.17]*12 + [16.19]*12 + [30.74]*12 + [31.17]*12 + [16.18]*12 + [17.11]*12 + [20.24]*12 + [24.94]*12 + [24.69]*12 + [26.48]*12 + [30.15]*12 + [23.14]*12 + [24.11]*12

# Initial state x(:,0) of first iteration
x_current = [320]*16

# Initial point around which to linearize
a_u = [310, 0.25, 0, 1, 0, 0]
a_x = [308]*4 + [313]*12

# ------------------------------------------------------
# System dynamics
# ------------------------------------------------------

def dynamics(u_t, x_t):
    
    # All heat transfers are 0 unless specified otherwise later
    Q_top_B = Q_bottom_B = Q_conv_B = Q_losses_B = [0]*4
    Q_top_S = Q_bottom_S = Q_conv_S = Q_losses_S = Q_R_S = [0]*12
    
    # For the buffer tank B
    #'''
    Q_top_B[0]      = f_approx(id="Q_top_B1", a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    Q_bottom_B[3]   = f_approx(id="Q_bottom_B4", a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    #'''
    for i in range(1,5):
        Q_conv_B[i-1] = f_approx(id="Q_conv_B{}".format(i), a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    
    # For the storage tank S
    #'''
    Q_top_S[0]      = f_approx(id="Q_top_S11", a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    Q_top_S[4]      = f_approx(id="Q_top_S21", a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    Q_top_S[8]      = f_approx(id="Q_top_S31", a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    Q_bottom_S[3]   = f_approx(id="Q_bottom_S14", a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    Q_bottom_S[7]   = f_approx(id="Q_bottom_S24", a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    Q_bottom_S[11]  = f_approx(id="Q_bottom_S34", a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]
    #'''
    for i in range(1,4):
        for j in range(1,5):
            Q_conv_S[4*(i-1)+(j-1)] = f_approx(id="Q_conv_S{}{}".format(i,j), a_u=a_u, a_x=a_x, y_u=u_t, y_x=x_t, real=False)[exact_or_approx]

    # Next state for buffer and storage
    const = delta_t_s / (m_layer * cp)
    x_plus_B = [x_t[i] + const * (Q_top_B[i] + Q_bottom_B[i] + Q_conv_B[i] - Q_losses_B[i]) for i in range(4)]
    x_plus_S = [x_t[i] + const * (Q_top_S[i] + Q_bottom_S[i] + Q_conv_S[i] - Q_losses_S[i] + Q_R_S[i]) for i in range(12)]

    # Bring everything together
    x_plus = []
    for i in range(len(x_plus_B)): x_plus = casadi.vertcat(x_plus, x_plus_B[i])
    for i in range(len(x_plus_S)): x_plus = casadi.vertcat(x_plus, x_plus_S[i])
    
    return x_plus

# ------------------------------------------------------
# Constraints
# ------------------------------------------------------

# Bounds constraints for u
for t in range(N):

    # T_sup_HP
    opti.subject_to(u[0,t] >= 273+30)
    opti.subject_to(u[0,t] <= 273+65)
    
    # m_stor
    opti.subject_to(u[1,t] >= 0)
    opti.subject_to(u[1,t] <= 0.5)
    
    # delta terms
    for i in range(2,6):
        opti.subject_to(u[i,t] >= 0)
        opti.subject_to(u[i,t] <= 1)

# Bounds constraints for x
for t in range(N+1):
    for i in range(16):
        opti.subject_to(x[i,t] >= T_w_min)
        opti.subject_to(x[i,t] <= T_w_max)
        
# Initial state
opti.subject_to(x[:,0] == x_0)

# Additional constraints
for t in range(N):
    
    # Heat pump operation
    opti.subject_to(f_approx(id="Q_HP", a_u=a_u, a_x=a_x, y_u=u[:,t], y_x=x[:,t], real=False)[exact_or_approx] >= Q_HP_min * u[4,t])
    opti.subject_to(f_approx(id="Q_HP", a_u=a_u, a_x=a_x, y_u=u[:,t], y_x=x[:,t], real=False)[exact_or_approx] <= Q_HP_max)
    
    # Load supply temperature
    opti.subject_to(f_approx(id="T_sup_load", a_u=a_u, a_x=a_x, y_u=u[:,t], y_x=x[:,t], real=False)[exact_or_approx] >= T_sup_load_min)
    
    # Mass flow rates
    opti.subject_to(f_approx(id="m_buffer", a_u=a_u, a_x=a_x, y_u=u[:,t], y_x=x[:,t], real=False)[exact_or_approx] >= 0)
    
    # Operational constraint (charging is only possible if the heat pump is on)
    opti.subject_to(u[2,t] <= u[4,t])
    
    # System dynamics
    opti.subject_to(x[:,t+1] == dynamics(u[:,t], x[:,t]))

# ------------------------------------------------------
# Objective
# ------------------------------------------------------

# Define objective
obj = sum(\
c_el[t] * f_approx(id="Q_HP", a_u=a_u, a_x=a_x, y_u=u[:,t], y_x=x[:,t], real=False)[exact_or_approx] \
for t in range(N))

# Set objective
opti.minimize(obj)

# ------------------------------------------------------
# MPC
# ------------------------------------------------------

print("Solving optimisation problem...\n")

for t in range(num_iterations):

    # ------------------------------------------------------
    # Set parameter values
    # ------------------------------------------------------

    opti.set_value(x_0, x_current)
    opti.set_value(c_el, c_el_all[t:t+N])

    # ------------------------------------------------------
    # Solving
    # ------------------------------------------------------

    # Solving the optimisation problem
    if GUROBI:  opti.solver('gurobi', solver_opts)
    else:       opti.solver('ipopt', solver_opts)
    sol = opti.solve()

    # Get optimal u and x
    u_optimal = sol.value(u)
    x_optimal = sol.value(x)
    
    # Implement u_0*, get corresponding next state
    x_1 = get_exact.x_1(u_optimal[:,0], x_optimal[:,0])
    x_current = x_1
    
    # ------------------------------------------------------
    # Prints
    # ------------------------------------------------------
    
    # Print iteration and simulated time
    hours = int(t*delta_t_h)
    minutes = round((t*delta_t_h-int(t*delta_t_h))*60)
    print("Iteration {} ({}h{}min)".format(t+1, hours, minutes))
    
    # Print state, u0*, next state
    print("-----------------------------------------------------")
    print("x_0 = {}".format([round(x,2) for x in x_optimal[:,0]]))
    print("u_0* = {}".format([round(x,2) for x in u_optimal[:,0]]))
    print("x_1_approx = {}".format([round(x,2) for x in x_optimal[:,1]]))
    print("x_1_exact = {}".format(x_1))
    print("-----------------------------------------------------\n")

    
