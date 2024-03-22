import casadi
import numpy as np
import time
import forecasts
from functions import get_function

# ------------------------------------------------------
# Constants
# ------------------------------------------------------

# Load
T_sup_load_min = 273 + 38 #K

# Tanks
A = 0.45 #m2
z = 0.25 #m
rho = 997 #kg/m3
m_layer = rho*A*z #kg (112kg)
T_w_min = 273 + 35 #K
T_w_max = 273 + 80 #K

# Heat pump
Q_HP_min = 8000 #W

# Other
cp = 4187 #J/kgK

# Time step
delta_t_m = 4
delta_t_h = delta_t_m/60
delta_t_s = delta_t_m*60

# ------------------------------------------------------
# System dynamics
# ------------------------------------------------------

def x_dot(u_t, x_t, t, sequence, iter):

    # All heat transfers are initialized at 0
    Q_top_B, Q_bottom_B, Q_conv_B, Q_losses_B = [0]*4, [0]*4, [0]*4, [0]*4
    Q_top_S, Q_bottom_S, Q_conv_S, Q_losses_S, Q_R_S = [0]*12, [0]*12, [0]*12, [0]*12, [0]*12
    
    # For the buffer tank B
    Q_top_B[0] = get_function("Q_top_B", u_t, x_t, t, sequence, iter)
    Q_bottom_B[3] = get_function("Q_bottom_B", u_t, x_t, t, sequence, iter)
    Q_conv_B = [get_function(f"Q_conv_B{i}", u_t, x_t, t, sequence, iter) for i in range(1,5)]

    # For the storage tanks S1, S2, S3
    Q_top_S[0] = get_function("Q_top_S1", u_t, x_t, t, sequence, iter)
    Q_top_S[4] = get_function("Q_top_S2", u_t, x_t, t, sequence, iter)
    Q_top_S[8] = get_function("Q_top_S3", u_t, x_t, t, sequence, iter)
    Q_bottom_S[3] = get_function("Q_bottom_S1", u_t, x_t, t, sequence, iter)
    Q_bottom_S[7] = get_function("Q_bottom_S2", u_t, x_t, t, sequence, iter)
    Q_bottom_S[11] = get_function("Q_bottom_S3", u_t, x_t, t, sequence, iter)
    for i in range(1,4):
        for j in range(1,5):
            Q_conv_S[4*(i-1)+(j-1)] = get_function(f"Q_conv_S{i}{j}", u_t, x_t, t, sequence, iter)
            
    # For the resistive elements
    # Q_R_S = ([0] + [4500*u_t[5]] + [0] + [4500*u_t[5]])*3

    f_B = [1/(m_layer*cp) * (Q_top_B[i] + Q_bottom_B[i] + Q_conv_B[i] - Q_losses_B[i]) for i in range(4)]
    f_S = [1/(m_layer*cp) * (Q_top_S[i] + Q_bottom_S[i] + Q_conv_S[i] - Q_losses_S[i] + Q_R_S[i]) for i in range(12)]
        
    # Bring everything together (need to use casadi.vertcat for symbolic values)
    dynamics_f = []
    for i in range(len(f_B)): dynamics_f = casadi.vertcat(dynamics_f, f_B[i])
    for i in range(len(f_S)): dynamics_f = casadi.vertcat(dynamics_f, f_S[i])
        
    return dynamics_f

# ------------------------------------------------------
# Optimize over the next N time steps
# ------------------------------------------------------

def optimize_N_steps(x_0, iter, pb_type, sequence, warm_start, PRINT):

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
    T_OA, COP1, Q_HP_max = forecasts.get_T_OA(iter, iter+N, delta_t_h)

    # ------------------------------------------------------
    # Constraints
    # ------------------------------------------------------
    
    if PRINT: print("Setting up the MINLP with the requested sequence...")
    
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
        
        # Just a print
        if PRINT and t%15==0:
            section_time = (section+int(iter/15))%24
            section_str = f"0{section_time}" if section_time<10 else f"{section_time}"
            section_1_str = f"0{section_time-1}" if section_time<11 else f"{section_time-1}"
            if section_time == 0: section_1_str = "23"
            print(f"{section_1_str}h-{section_str}h: {sequence[f'combi{section}']} ({round(c_el[t]*100*1000)} cts/kWh)")
            
        # ----- Non linear constraints -----
        
        # Heat pump operation
        opti.subject_to(get_function("Q_HP_nodelta", u[:,t], x[:,t], t, sequence, iter) >= Q_HP_min * u[4,t])
        opti.subject_to(get_function("Q_HP_nodelta", u[:,t], x[:,t], t, sequence, iter) <= Q_HP_max[t])
        
        # Load supply temperature
        opti.subject_to(get_function("T_sup_load", u[:,t], x[:,t], t, sequence, iter) >= T_sup_load_min)
        
        # Mass flow rates
        opti.subject_to(get_function("m_buffer", u[:,t], x[:,t], t, sequence, iter) >= 0)
        
        # System dynamics
        if pb_type['integration'] == "euler":
            opti.subject_to(x[:,t+1] == x[:,t] + delta_t_s * x_dot(u[:,t], x[:,t], t, sequence, iter))
        
        elif pb_type['integration'] == "rk2":
            k1 = x_dot(u[:,t], x[:,t], t, sequence, iter)
            k2 = x_dot(u[:,t], x[:,t] + delta_t_s/2 * k1, t, sequence, iter)
            opti.subject_to(x[:,t+1] == x[:,t] + delta_t_s*k2)
            
        elif pb_type['integration'] == "rk4":
            k1 = x_dot(u[:,t], x[:,t], t, sequence, iter)
            k2 = x_dot(u[:,t], x[:,t] + delta_t_s/2 * k1, t, sequence, iter)
            k3 = x_dot(u[:,t], x[:,t] + delta_t_s/2 * k2, t, sequence, iter)
            k4 = x_dot(u[:,t], x[:,t] + delta_t_s * k3, t, sequence, iter)
            opti.subject_to(x[:,t+1] == x[:,t] + delta_t_s*(k1/6 + k2/3 + k3/3 + k4/6))
            
    # ------------------------------------------------------
    # Objective
    # ------------------------------------------------------

    # With COP(T_OA, T_OA^2, T_HP_sup) (comment for COP(T_OA) only)
    B_0, B_1, B_2, B_3 = 11.581585, -0.086161, 0.000140, 0.005700
    COP1 = [B_0 + B_1*T_OA[t] + B_2*T_OA[t]**2 + B_3*u[0,t] for t in range(N)]
    
    obj = sum(c_el[t] * delta_t_h * get_function("Q_HP", u[:,t], x[:,t], t, sequence, iter)*COP1[t] for t in range(N))
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
