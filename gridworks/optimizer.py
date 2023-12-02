import casadi
import numpy as np
import time
import functions, forecasts
from functions import get_function

# ------------------------------------------------------
# Constants
# ------------------------------------------------------

# Heat pump
Q_HP_min = 0 #8000 #W
Q_HP_max = 14000 #W

# Load
T_sup_load_min = 273 + 38 #K

# Tanks
A = 0.45 #m2
z = 0.25 #m
rho = 997 #kg/m3
m_layer = rho*A*z #kg (112kg)
T_w_min = 273 + 10 #K
T_w_max = 273 + 80 #K

# Other
cp = 4187 #J/kgK


# ------------------------------------------------------
# System dynamics
# ------------------------------------------------------
'''
INPUTS:
- The input at time step t: u(t)
- The state at time step t: x(t)
- The point around which to linearize: a
- Real values or symbolic: real
- Linearized problem or not: approx

OUTPUTS:
- The state at time step t+1: x(t+1)
'''
def dynamics(u_t, x_t, a, real, approx, delta_t_s):

    # All heat transfers are 0 unless specified otherwise later
    Q_top_B     = [0]*4
    Q_bottom_B  = [0]*4
    Q_conv_B    = [0]*4
    Q_losses_B  = [0]*4
    
    Q_top_S     = [0]*12
    Q_bottom_S  = [0]*12
    Q_conv_S    = [0]*12
    Q_losses_S  = [0]*12
    Q_R_S       = [0]*12
    
    # For the buffer tank B
    Q_top_B[0]      = get_function("Q_top_B", u_t, x_t, a, real, approx)
    Q_bottom_B[3]   = get_function("Q_bottom_B", u_t, x_t, a, real, approx)
    for i in range(1,5):
        Q_conv_B[i-1] = get_function(f"Q_conv_B{i}", u_t, x_t, a, real, approx)

    # For the storage tanks S1, S2, S3
    Q_top_S[0]      = get_function("Q_top_S1", u_t, x_t, a, real, approx)
    Q_top_S[4]      = get_function("Q_top_S2", u_t, x_t, a, real, approx)
    Q_top_S[8]      = get_function("Q_top_S3", u_t, x_t, a, real, approx)
    Q_bottom_S[3]   = get_function("Q_bottom_S1", u_t, x_t, a, real, approx)
    Q_bottom_S[7]   = get_function("Q_bottom_S2", u_t, x_t, a, real, approx)
    Q_bottom_S[11]  = get_function("Q_bottom_S3", u_t, x_t, a, real, approx)
    for i in range(1,4):
        for j in range(1,5):
            Q_conv_S[4*(i-1)+(j-1)] = get_function(f"Q_conv_S{i}{j}", u_t, x_t, a, real, approx)

    # Compute the next state for buffer and storage tank layers
    const = delta_t_s / (m_layer * cp)
    x_plus_B = [x_t[i] + const * (Q_top_B[i] + Q_bottom_B[i] + Q_conv_B[i] - Q_losses_B[i]) for i in range(4)]
    x_plus_S = [x_t[i+4] + const * (Q_top_S[i] + Q_bottom_S[i] + Q_conv_S[i] - Q_losses_S[i] + Q_R_S[i]) for i in range(12)]
    
    # Bring everything together (need to use casadi.vertcat for symbolic values)
    x_plus = []
    for i in range(len(x_plus_B)): x_plus = casadi.vertcat(x_plus, x_plus_B[i])
    for i in range(len(x_plus_S)): x_plus = casadi.vertcat(x_plus, x_plus_S[i])
        
    return x_plus_B + x_plus_S if real else x_plus


# ------------------------------------------------------
# Optimize over the next steps
# ------------------------------------------------------
'''
GOAL:
Find the feasible sequence u={u_0,...,u_N-1} that minimizes the objective

INPUTS:
- x_0: The current state
- a: The point around which to linearize
- iter: The iteration number of the MPC
- pb_type: A dictionnary with problem type
--- linearized: True if linearized problem, False if not
--- mixed-integer: True if mixed integer variables, False if continuous
--- gurobi: True if solver is gurobi, False if it is ipopt
--- horizon: The horizon of the MPC (N)
- case: the values of the delta terms if solving a single combination

OUTPUTS:
- u_optimal: The optimal input sequence for the next N steps
- x_optimal: The corresponding sequence of states for the next N steps
'''
def optimize_N_steps(x_0, a, iter, pb_type, case):
    ''' Here '''

    # Get the time step
    delta_t_m = pb_type['time_step'] #min
    delta_t_s = delta_t_m*60 #sec
    delta_t_h = delta_t_m/60 #hours

    # Print iteration and simulated time
    hours = int(iter*delta_t_h)
    minutes = round((iter*delta_t_h-int(iter*delta_t_h))*60)
    print("\n-----------------------------------------------------")
    print(f"Iteration {iter+1} ({hours}h{minutes}min)")
    print("-----------------------------------------------------\n")

    # ------------------------------------------------------
    # Variables
    # ------------------------------------------------------

    # Initialize CasADi
    opti = casadi.Opti('conic') if pb_type['gurobi'] else casadi.Opti()
    
    # Get horizon
    N = pb_type['horizon']

    # Define state and input variables
    u = opti.variable(6, N)     # T_sup_HP, m_stor, d_ch, d_bu, d_HP, d_R
    x = opti.variable(16, N+1)  # T_B1,...,T_B4, T_S11,...,T_S14, T_S21,...,T_S24, T_S31,...,T_S34

    # All variables are continuous except d_ch, d_bu and d_HP (binary)
    discrete_var = ([0]*2 + [1]*3 + [0]) * N
    discrete_var += [0]*16 * (N+1)

    # ------------------------------------------------------
    # Problem type and solver
    # ------------------------------------------------------

    if pb_type['gurobi']:
        if pb_type['mixed-integer']:
            solver_opts = {'discrete':discrete_var, 'gurobi.OutputFlag':0}
            opti.solver('gurobi', solver_opts)
        else:
            solver_opts = {'gurobi.OutputFlag':0}
            opti.solver('gurobi', solver_opts)
        
    else:
        if pb_type['mixed-integer']:
            solver_opts = {'discrete': discrete_var, 'bonmin.tol': 1e-4}
            opti.solver('bonmin', solver_opts)
        else:
            solver_opts = {'ipopt.print_level': 0, 'print_time': 0, 'ipopt.tol': 1e-10}
            opti.solver('ipopt', solver_opts)
                
    approx = True if pb_type['linearized'] else False
    real = False # False in this file since we are defining the optimization problem
    
    # ------------------------------------------------------
    # Parameters
    # ------------------------------------------------------

    # Electricity prices for the next N steps
    c_el = forecasts.get_c_el(iter, iter+N, delta_t_h)
    
    # Load mass flow rate for the next N steps
    m_load = forecasts.get_m_load(iter, iter+N, delta_t_h)

    # ------------------------------------------------------
    # Compute f(a) and grad_f(a) for all non linear terms
    # ------------------------------------------------------
        
    if approx:
        print("Computing all f(a) and grad_f(a)...")
        start_time = time.time()
        a = {
        'values': a,
        'functions_a': functions.get_all_f(a),
        'gradients_a': functions.get_all_grad_f(a)
        }
        #print("Done in {} seconds.".format(round(time.time()-start_time,1)))

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
        
        ''' Here '''
        # delta terms if there is a specific case
        if not case['general']:
            opti.subject_to(u[2,t] == case['d_ch'])
            opti.subject_to(u[3,t] == case['d_bu'])
            opti.subject_to(u[4,t] == case['d_HP'])
            opti.subject_to(u[5,t] == case['d_R'])
        
        # delta terms if there is no specific case
        else:
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
    print("Setting all non linear constraints...")
    start_time = time.time()
    for t in range(N):
            
        # Heat pump operation
        opti.subject_to(get_function("Q_HP", u[:,t], x[:,t], a, real, approx) >= Q_HP_min * u[4,t])
        opti.subject_to(get_function("Q_HP", u[:,t], x[:,t], a, real, approx) <= Q_HP_max)
        
        # Load supply temperature
        opti.subject_to(get_function("T_sup_load", u[:,t], x[:,t], a, real, approx) >= T_sup_load_min)
        
        # Mass flow rates
        opti.subject_to(get_function("m_buffer", u[:,t], x[:,t], a, real, approx) >= 0)
        
        # Operational constraint (charging is only possible if the heat pump is on)
        opti.subject_to(u[2,t] <= u[4,t])
        
        # System dynamics
        opti.subject_to(x[:,t+1] == dynamics(u[:,t], x[:,t], a, real, approx, delta_t_s))
    #print("Done in {} seconds.\n".format(round(time.time()-start_time,1)))

    # ------------------------------------------------------
    # Objective
    # ------------------------------------------------------

    # Define objective as the cost of used electricity over the next N steps
    obj = sum(c_el[t] * delta_t_h * get_function("Q_HP", u[:,t], x[:,t], a, real, approx) for t in range(N))

    # Set objective
    opti.minimize(obj)

    # ------------------------------------------------------
    # Solve
    # ------------------------------------------------------
    
    # Solve the optimisation problem
    print("Solving the optimization problem...")
    start_time = time.time()
    sol = opti.solve()
    #print("Done in {} seconds.".format(round(time.time()-start_time,1)))

    # Get optimal u=u_0*,...,u_N-1*
    u_optimal = sol.value(u)
   
    # Get corresponding states x0,...,xN
    x_optimal = sol.value(x)

    # Return optimal sequence of u and x
    return u_optimal, x_optimal
