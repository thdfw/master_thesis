import casadi
import numpy as np
import time
import forecasts
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

def dynamics(u_t, x_t, delta_t_s, t, sequence, iter):

    # Time step in hours
    delta_t_h = delta_t_s / 3600

    # All heat transfers are initialized at 0
    Q_top_B, Q_bottom_B, Q_conv_B, Q_losses_B = [0]*4, [0]*4, [0]*4, [0]*4
    Q_top_S, Q_bottom_S, Q_conv_S, Q_losses_S, Q_R_S = [0]*12, [0]*12, [0]*12, [0]*12, [0]*12
    
    # For the buffer tank B
    Q_top_B[0] = get_function("Q_top_B", u_t, x_t, t, sequence, iter, delta_t_h)
    Q_bottom_B[3] = get_function("Q_bottom_B", u_t, x_t, t, sequence, iter, delta_t_h)
    Q_conv_B = [get_function(f"Q_conv_B{i}", u_t, x_t, t, sequence, iter, delta_t_h) for i in range(1,5)]

    # For the storage tanks S1, S2, S3
    Q_top_S[0] = get_function("Q_top_S1", u_t, x_t, t, sequence, iter, delta_t_h)
    Q_top_S[4] = get_function("Q_top_S2", u_t, x_t, t, sequence, iter, delta_t_h)
    Q_top_S[8] = get_function("Q_top_S3", u_t, x_t, t, sequence, iter, delta_t_h)
    Q_bottom_S[3] = get_function("Q_bottom_S1", u_t, x_t, t, sequence, iter, delta_t_h)
    Q_bottom_S[7] = get_function("Q_bottom_S2", u_t, x_t, t, sequence, iter, delta_t_h)
    Q_bottom_S[11] = get_function("Q_bottom_S3", u_t, x_t, t, sequence, iter, delta_t_h)
    for i in range(1,4):
        for j in range(1,5):
            Q_conv_S[4*(i-1)+(j-1)] = get_function(f"Q_conv_S{i}{j}", u_t, x_t, t, sequence, iter, delta_t_h)
            
    # For the resistive elements
    # Q_R_S = ([0] + [4500*u_t[5]] + [0] + [4500*u_t[5]])*3

    # Compute the next state
    const = delta_t_s / (m_layer * cp)
    x_plus_B = [x_t[i] + const * (Q_top_B[i] + Q_bottom_B[i] + Q_conv_B[i] - Q_losses_B[i]) for i in range(4)]
    x_plus_S = [x_t[i+4] + const * (Q_top_S[i] + Q_bottom_S[i] + Q_conv_S[i] - Q_losses_S[i] + Q_R_S[i]) for i in range(12)]
    
    # Bring everything together (need to use casadi.vertcat for symbolic values)
    x_plus = []
    for i in range(len(x_plus_B)): x_plus = casadi.vertcat(x_plus, x_plus_B[i])
    for i in range(len(x_plus_S)): x_plus = casadi.vertcat(x_plus, x_plus_S[i])
        
    return x_plus

# ------------------------------------------------------
# Optimize over the next N time steps
# ------------------------------------------------------

def optimize_N_steps(x_0, iter, pb_type, sequence, warm_start, PRINT):

    # ------------------------------------------------------
    # Read problem type
    # ------------------------------------------------------
    
    # Time step
    delta_t_m = pb_type['time_step'] #min
    delta_t_s = delta_t_m*60 #sec
    delta_t_h = delta_t_m/60 #hours
    
    # Horizon
    N = pb_type['horizon']

    # ------------------------------------------------------
    # Variables
    # ------------------------------------------------------

    # Initialize CasADi
    opti = casadi.Opti('conic') if pb_type['gurobi'] else casadi.Opti()

    # Define state and input variables
    u = opti.variable(6, N)     # T_sup_HP, m_stor, d_ch, d_bu, d_HP, d_R
    x = opti.variable(16, N+1)  # T_B1,...,T_B4, T_S11,...,T_S14, T_S21,...,T_S24, T_S31,...,T_S34

    # All variables are continuous except d_ch, d_bu, d_HP (binary)
    discrete_var = ([0]*2 + [1]*3 + [0]) * N
    discrete_var += [0]*16 * (N+1)

    # ------------------------------------------------------
    # Solver and options
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
            solver_opts = {'ipopt.print_level': 0, 'print_time': 0, 'ipopt.tol': 1e-10, 'ipopt.max_iter': 1500}
            opti.solver('ipopt', solver_opts)
                    
    # ------------------------------------------------------
    # Forecasts
    # ------------------------------------------------------

    # Electricity prices for the next N steps
    c_el = forecasts.get_c_el(iter, iter+N, delta_t_h)
    
    # Load mass flow rate for the next N steps
    m_load = forecasts.get_m_load(iter, iter+N, delta_t_h)
    
    # 1/COP and Q_HP_max for the next N steps
    COP1, Q_HP_max = forecasts.get_T_OA(iter, iter+N, delta_t_h)

    # ------------------------------------------------------
    # Constraints
    # ------------------------------------------------------
    
    if PRINT: print("Setting all constraints with the requested sequence...")
    
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
        section = int(t/15)+1
        [d_ch, d_bu, d_HP] = sequence[f'combi{section}']
        opti.subject_to(u[2,t] == d_ch)
        opti.subject_to(u[3,t] == d_bu)
        opti.subject_to(u[4,t] == d_HP)
        
        if PRINT and t%15==0:
            print(f"{section-1}h-{section}h: {sequence[f'combi{section}']}")
            
        # ----- Non linear constraints -----
        
        # Heat pump operation
        if d_HP == 1:
            opti.subject_to(get_function("Q_HP", u[:,t], x[:,t], t, sequence, iter, delta_t_h) >= Q_HP_min * u[4,t])
            opti.subject_to(get_function("Q_HP", u[:,t], x[:,t], t, sequence, iter, delta_t_h) <= Q_HP_max[t])
        
        # Load supply temperature
        opti.subject_to(get_function("T_sup_load", u[:,t], x[:,t], t, sequence, iter, delta_t_h) >= T_sup_load_min)
        
        # Mass flow rates
        opti.subject_to(get_function("m_buffer", u[:,t], x[:,t], t, sequence, iter, delta_t_h) >= 0)
        
        # System dynamics
        opti.subject_to(x[:,t+1] == dynamics(u[:,t], x[:,t], delta_t_s, t, sequence, iter))
            
    # ------------------------------------------------------
    # Objective
    # ------------------------------------------------------

    # Cost of electricity used over the next N steps
    obj = sum(c_el[t] * delta_t_h * get_function("Q_HP", u[:,t], x[:,t], t, sequence, iter, delta_t_h)*COP1[t] for t in range(N))
    # Adding resistances: +27000*u[5,t]) for t in range(N))

    # Set objective
    opti.minimize(obj)

    # ------------------------------------------------------
    # Solve
    # ------------------------------------------------------
    
    # Use the provided warm start to initialize the solver
    opti.set_initial(u, warm_start['initial_u'])
    opti.set_initial(x, warm_start['initial_x'])
    
    # Solve the optimization problem
    if PRINT: print("\nSolving the optimization problem...")
    start_time = time.time()
    success, err_message = True, ""
    try:
        sol = opti.solve()
        if PRINT: print("Done in {} seconds.".format(round(time.time()-start_time)))
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

    return u_optimal, x_optimal, obj_optimal, err_message