import casadi
import numpy as np
import time
import functions, forecasts
from functions import get_function

# ------------------------------------------------------
# Constants
# ------------------------------------------------------

# Heat pump
Q_HP_min = 8000 #W

# Load
T_sup_load_min = 273 + 38 #K

# Tanks
A = 0.45 #m2
z = 0.25 #m
rho = 997 #kg/m3
m_layer = rho*A*z #kg (112kg)
T_w_min = 273 + 35 #K
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
def dynamics(u_t, x_t, a, real, approx, delta_t_s, t, sequence, iter):

    delta_t_h = delta_t_s / 3600

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
    Q_top_B[0]      = get_function("Q_top_B", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)
    Q_bottom_B[3]   = get_function("Q_bottom_B", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)
    for i in range(1,5):
        Q_conv_B[i-1] = get_function(f"Q_conv_B{i}", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)

    # For the storage tanks S1, S2, S3
    # Q_R_S           = ([0] + [4500*u_t[5]] + [0] + [4500*u_t[5]])*3
    Q_top_S[0]      = get_function("Q_top_S1", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)
    Q_top_S[4]      = get_function("Q_top_S2", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)
    Q_top_S[8]      = get_function("Q_top_S3", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)
    Q_bottom_S[3]   = get_function("Q_bottom_S1", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)
    Q_bottom_S[7]   = get_function("Q_bottom_S2", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)
    Q_bottom_S[11]  = get_function("Q_bottom_S3", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)
    for i in range(1,4):
        for j in range(1,5):
            Q_conv_S[4*(i-1)+(j-1)] = get_function(f"Q_conv_S{i}{j}", u_t, x_t, a, real, approx, t, sequence, iter, delta_t_h)

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
def optimize_N_steps(x_0, a, iter, pb_type, sequence, warm_start, PRINT):

    # Get the time step
    delta_t_m = pb_type['time_step'] #min
    delta_t_s = delta_t_m*60 #sec
    delta_t_h = delta_t_m/60 #hours

    # Print iteration and simulated time
    hours = int(iter*delta_t_h)
    minutes = round((iter*delta_t_h-int(iter*delta_t_h))*60)
    if PRINT:
        print("\n-----------------------------------------------------")
        print(f"Iteration {iter/15+1} ({hours}h{minutes}min)")
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
    
    # 1/COP and Q_HP_max
    COP1, Q_HP_max = forecasts.get_T_OA(iter, iter+N, delta_t_h)

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
    
    if PRINT: print("Setting all constraints with the requested sequence...")
    start_time = time.time()
    
    # ----- Initial state -----
    opti.subject_to(x[:,0] == x_0)
    
    # ----- Bounds on x -----
    for t in range(N+1):
        for i in range(16):
            opti.subject_to(x[i,t] >= T_w_min)
            opti.subject_to(x[i,t] <= T_w_max)

    # ----- Bounds on u -----
    for t in range(N):

        # T_sup_HP
        opti.subject_to(u[0,t] >= 273+30)
        opti.subject_to(u[0,t] <= 273+65)
        
        # m_stor
        opti.subject_to(u[1,t] >= 0)
        opti.subject_to(u[1,t] <= 0.5)
        
        # delta_R term
        opti.subject_to(u[5,t] >= 0)
        opti.subject_to(u[5,t] <= 1)
        
        # The other delta terms are fixed by the provided sequence
        if t>=0  and t<15: [d_ch, d_bu, d_HP] = sequence['combi1']
        if t>=15 and t<30: [d_ch, d_bu, d_HP] = sequence['combi2']
        if t>=30 and t<45: [d_ch, d_bu, d_HP] = sequence['combi3']
        if t>=45 and t<60: [d_ch, d_bu, d_HP] = sequence['combi4']
        if t>=60 and t<75: [d_ch, d_bu, d_HP] = sequence['combi5']
        if t>=75 and t<00: [d_ch, d_bu, d_HP] = sequence['combi6']
        if t>=90 and t<105: [d_ch, d_bu, d_HP] = sequence['combi7']
        if t>=105 and t<120: [d_ch, d_bu, d_HP] = sequence['combi8']

        opti.subject_to(u[2,t] == d_ch)
        opti.subject_to(u[3,t] == d_bu)
        opti.subject_to(u[4,t] == d_HP)
        
        if PRINT:
            if t==0:  print(f"0h-1h: {sequence['combi1']}")
            if t==15: print(f"1h-2h: {sequence['combi2']}")
            if t==30: print(f"2h-3h: {sequence['combi3']}")
            if t==45: print(f"3h-4h: {sequence['combi4']}")
            if t==60: print(f"4h-5h: {sequence['combi5']}")
            if t==75: print(f"5h-6h: {sequence['combi6']}")
            if t==90: print(f"6h-7h: {sequence['combi7']}")
            if t==105: print(f"7h-8h: {sequence['combi8']}\n")
            
        # ----- Non linear constraints -----
        
        # Heat pump operation
        if d_HP == 1:
            opti.subject_to(get_function("Q_HP", u[:,t], x[:,t], a, real, approx, t, sequence, iter, delta_t_h) >= Q_HP_min * u[4,t])
            opti.subject_to(get_function("Q_HP", u[:,t], x[:,t], a, real, approx, t, sequence, iter, delta_t_h) <= Q_HP_max[t])
        
        # Load supply temperature
        opti.subject_to(get_function("T_sup_load", u[:,t], x[:,t], a, real, approx, t, sequence, iter, delta_t_h) >= T_sup_load_min)
        
        # Mass flow rates
        opti.subject_to(get_function("m_buffer", u[:,t], x[:,t], a, real, approx, t, sequence, iter, delta_t_h) >= 0)
        
        # Operational constraint (charging is only possible if the heat pump is on)
        opti.subject_to(u[2,t] <= u[4,t])
        
        # System dynamics
        opti.subject_to(x[:,t+1] == dynamics(u[:,t], x[:,t], a, real, approx, delta_t_s, t, sequence, iter))
    #print("Done in {} seconds.\n".format(round(time.time()-start_time,1)))
            
    # ------------------------------------------------------
    # Objective
    # ------------------------------------------------------

    # Define objective as the cost of used electricity over the next N steps
    obj = sum(c_el[t] * delta_t_h * get_function("Q_HP", u[:,t], x[:,t], a, real, approx, t, sequence, iter, delta_t_h)*COP1[t] for t in range(N))
    # Adding resistances: +27000*u[5,t]) for t in range(N))

    # Set objective
    opti.minimize(obj)

    # ------------------------------------------------------
    # Solve
    # ------------------------------------------------------
    
    # Give the solver a warm start
    initial_u = warm_start['initial_u']
    initial_x = warm_start['initial_x']
    opti.set_initial(u, initial_u)
    opti.set_initial(x, initial_x)

    '''
    print("\n - - WARM START - - \n")
    print("X:")
    print(initial_x)
    print("\nU:")
    print(initial_u)
    '''
    
    # Solve the optimisation problem
    if PRINT: print("Solving the optimization problem...")
    start_time = time.time()
    success, err_message = True, ""
    try:
        sol = opti.solve()
        if PRINT: print("Done in {} seconds.".format(round(time.time()-start_time,1)))
    except Exception as e:
        success = False
        err_message = str(e).split()[-1]
        if PRINT: print(f"Failed to solve: {err_message}!")

    # Get optimal u=u_0*,...,u_N-1*
    u_optimal = sol.value(u) if success else np.nan

    # Get corresponding states x0,...,xN
    x_optimal = sol.value(x) if success else np.nan

    # Get the value of the objective at optimal
    obj_optimal = round(sol.value(obj),3) if success else 1e5

    # Return optimal sequence of u and x
    return u_optimal, x_optimal, obj_optimal, err_message
