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
def dynamics(u_t, x_t, a, real, approx, delta_t_s, t, sequence):

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
    Q_top_B[0]      = get_function("Q_top_B", u_t, x_t, a, real, approx, t, sequence)
    Q_bottom_B[3]   = get_function("Q_bottom_B", u_t, x_t, a, real, approx, t, sequence)
    for i in range(1,5):
        Q_conv_B[i-1] = get_function(f"Q_conv_B{i}", u_t, x_t, a, real, approx, t, sequence)

    # For the storage tanks S1, S2, S3
    Q_top_S[0]      = get_function("Q_top_S1", u_t, x_t, a, real, approx, t, sequence)
    Q_top_S[4]      = get_function("Q_top_S2", u_t, x_t, a, real, approx, t, sequence)
    Q_top_S[8]      = get_function("Q_top_S3", u_t, x_t, a, real, approx, t, sequence)
    Q_bottom_S[3]   = get_function("Q_bottom_S1", u_t, x_t, a, real, approx, t, sequence)
    Q_bottom_S[7]   = get_function("Q_bottom_S2", u_t, x_t, a, real, approx, t, sequence)
    Q_bottom_S[11]  = get_function("Q_bottom_S3", u_t, x_t, a, real, approx, t, sequence)
    for i in range(1,4):
        for j in range(1,5):
            Q_conv_S[4*(i-1)+(j-1)] = get_function(f"Q_conv_S{i}{j}", u_t, x_t, a, real, approx, t, sequence)

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
def optimize_N_steps(x_0, a, iter, pb_type, sequence, PRINT):

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
        
        opti.subject_to(u[2,t] == d_ch)
        opti.subject_to(u[3,t] == d_bu)
        opti.subject_to(u[4,t] == d_HP)
        
        if PRINT:
            if t==0:  print(f"0h00-0h30: {sequence['combi1']}")
            if t==15: print(f"0h30-1h00: {sequence['combi2']}")
            if t==30: print(f"1h00-1h30: {sequence['combi3']}")
            if t==45: print(f"1h30-2h00: {sequence['combi4']}\n")
            
        # ----- Non linear constraints -----
        
        # Heat pump operation
        if d_HP == 1:
            opti.subject_to(get_function("Q_HP", u[:,t], x[:,t], a, real, approx, t, sequence) >= Q_HP_min * u[4,t])
            opti.subject_to(get_function("Q_HP", u[:,t], x[:,t], a, real, approx, t, sequence) <= Q_HP_max)
        
        # Load supply temperature
        opti.subject_to(get_function("T_sup_load", u[:,t], x[:,t], a, real, approx, t, sequence) >= T_sup_load_min)
        
        # Mass flow rates
        opti.subject_to(get_function("m_buffer", u[:,t], x[:,t], a, real, approx, t, sequence) >= 0)
        
        # Operational constraint (charging is only possible if the heat pump is on)
        opti.subject_to(u[2,t] <= u[4,t])
        
        # System dynamics
        opti.subject_to(x[:,t+1] == dynamics(u[:,t], x[:,t], a, real, approx, delta_t_s, t, sequence))
    #print("Done in {} seconds.\n".format(round(time.time()-start_time,1)))
            
    # ------------------------------------------------------
    # Objective
    # ------------------------------------------------------

    # Define objective as the cost of used electricity over the next N steps
    obj = sum(c_el[t] * delta_t_h * get_function("Q_HP", u[:,t], x[:,t], a, real, approx, t, sequence) for t in range(N))

    # Set objective
    opti.minimize(obj)

    # ------------------------------------------------------
    # Solve
    # ------------------------------------------------------
    
    # Set initial guesses for u and x
    initial_x = [[316.5117, 315.498, 314.7902, 314.3121, 314.0194, 313.8652, 313.8005, 313.7812, 313.7739, 315.2907, 316.2965, 316.9475, 317.3544, 317.6115, 317.7967, 317.9663, 317.9172, 317.8635, 317.8053, 317.7429, 317.6761, 317.6046, 317.5277, 317.4448, 317.3547, 317.2562, 317.1477, 317.0277, 316.8944, 316.746, 316.5805, 316.396, 316.1903, 315.9614, 315.707, 315.4246, 315.1117, 314.7654, 314.3824, 313.9588, 313.49, 312.9697, 312.39, 311.7394, 311.0002, 310.1425],
    [314.6804, 315.2681, 315.3419, 315.1648, 314.8911, 314.6114, 314.3719, 314.1885, 314.0577, 313.9666, 314.3916, 315.003, 315.6271, 316.1815, 316.6405, 317.0116, 316.9456, 316.8756, 316.7999, 316.7162, 316.6219, 316.5143, 316.3905, 316.2478, 316.0839, 315.8968, 315.6846, 315.446, 315.18, 314.886, 314.5634, 314.2122, 313.8323, 313.4239, 312.9873, 312.5226, 312.0301, 311.5097, 310.9612, 310.3843, 309.7776, 309.1394, 308.4665, 307.7537, 306.9919, 306.1644],
    [314.2033, 314.3564, 314.649, 314.8714, 314.9656, 314.9417, 314.8357, 314.6868, 314.5269, 314.3763, 314.2448, 314.2919, 314.5202, 314.8755, 315.2947, 315.7266, 315.6798, 315.5895, 315.4526, 315.2678, 315.0353, 314.7565, 314.434, 314.0708, 313.6707, 313.2378, 312.7761, 312.2899, 311.7833, 311.26, 310.7238, 310.1781, 309.6257, 309.0694, 308.5116, 307.9543, 307.3992, 306.8477, 306.3009, 305.7594, 305.2236, 304.6935, 304.1682, 303.6464, 303.1246, 302.5969],
    [314.3921, 314.3315, 314.3395, 314.4388, 314.5777, 314.7022, 314.7791, 314.7972, 314.7618, 314.6864, 314.5869, 314.4771, 314.4177, 314.4506, 314.5869, 314.8141, 314.0475, 313.2644, 312.477, 311.6952, 310.9268, 310.1779, 309.453, 308.7557, 308.0883, 307.4524, 306.8488, 306.2779, 305.7395, 305.233, 304.7575, 304.3122, 303.8957, 303.5067, 303.1439, 302.806, 302.4914, 302.199, 301.9272, 301.6749, 301.4406, 301.2231, 301.0212, 300.8334, 300.6582, 300.4936],
    [308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.8, 308.5886, 308.3952, 308.2173, 308.0529, 307.9003, 307.7585, 307.6263, 307.5028, 307.3875, 307.2796, 307.1785, 307.0837, 306.9948, 306.9113, 306.8329, 306.7592, 306.69, 306.6249, 306.5637, 306.5063, 306.4526, 306.4024, 306.356, 306.3133, 306.2747, 306.2407, 306.2122, 306.1904, 306.1775, 306.1775],
    [307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.5, 307.3699, 307.2481, 307.1344, 307.0284, 306.9295, 306.8374, 306.7514, 306.6712, 306.5963, 306.5261, 306.4601, 306.3981, 306.3396, 306.2841, 306.2314, 306.1812, 306.1331, 306.087, 306.0427, 306.0001, 305.9591, 305.9199, 305.8825, 305.8472, 305.8145, 305.785, 305.7597, 305.7401, 305.7284, 305.7284],
    [306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.7, 306.6024, 306.515, 306.4361, 306.3644, 306.2989, 306.2387, 306.1829, 306.1307, 306.0816, 306.0349, 305.9901, 305.9467, 305.9043, 305.8626, 305.8212, 305.78, 305.7387, 305.6974, 305.6559, 305.6143, 305.5728, 305.5317, 305.4913, 305.4522, 305.4152, 305.3812, 305.3516, 305.3283, 305.3143, 305.3143],
    [306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.1, 306.0512, 306.0062, 305.9642, 305.9247, 305.8867, 305.8498, 305.8132, 305.7765, 305.7392, 305.7009, 305.6612, 305.6199, 305.5768, 305.5317, 305.4847, 305.4357, 305.3849, 305.3324, 305.2785, 305.2236, 305.1681, 305.1126, 305.0579, 305.0048, 304.9545, 304.9083, 304.8682, 304.8368, 304.8179, 304.8179],
    [305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.8, 305.7675, 305.7357, 305.7035, 305.6698, 305.6339, 305.5951, 305.5531, 305.5076, 305.4583, 305.4051, 305.3482, 305.2875, 305.2231, 305.1555, 305.0848, 305.0114, 304.9357, 304.8584, 304.7799, 304.701, 304.6223, 304.5447, 304.4692, 304.397, 304.3294, 304.2681, 304.2155, 304.1747, 304.1503, 304.1503],
    [305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.6, 305.5675, 305.528, 305.4816, 305.4285, 305.3687, 305.3025, 305.2302, 305.1522, 305.0688, 304.9806, 304.888, 304.7916, 304.692, 304.5898, 304.4856, 304.3802, 304.2741, 304.1681, 304.0631, 303.9596, 303.8587, 303.7612, 303.6681, 303.5806, 303.5, 303.428, 303.367, 303.3202, 303.2925, 303.2925],
    [305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.4, 305.3187, 305.229, 305.1316, 305.0269, 304.9157, 304.7988, 304.677, 304.5512, 304.4221, 304.2906, 304.1576, 304.0237, 303.8898, 303.7565, 303.6246, 303.4948, 303.3677, 303.244, 303.1241, 303.0089, 302.8989, 302.7948, 302.6973, 302.6072, 302.5256, 302.4539, 302.3939, 302.3483, 302.3215, 302.3215],
    [304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.9, 304.7536, 304.6005, 304.4422, 304.2801, 304.1158, 303.9503, 303.7849, 303.6206, 303.4584, 303.2989, 303.143, 302.9911, 302.8439, 302.7017, 302.5649, 302.4339, 302.309, 302.1903, 302.0781, 301.9726, 301.874, 301.7825, 301.6985, 301.6222, 301.5543, 301.4954, 301.4467, 301.4101, 301.3888, 301.3888],
    [304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 304.0, 303.7886, 303.5798, 303.3751, 303.176, 302.9834, 302.798, 302.6203, 302.4508, 302.2895, 302.1366, 301.9921, 301.8558, 301.7278, 301.6078, 301.4956, 301.3909, 301.2937, 301.2036, 301.1203, 301.0438, 300.9738, 300.9101, 300.8527, 300.8015, 300.7566, 300.7182, 300.6869, 300.6636, 300.6502, 300.6502],
    [302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.7, 302.4723, 302.2605, 302.0641, 301.8823, 301.7146, 301.5602, 301.4183, 301.288, 301.1687, 301.0595, 300.9597, 300.8687, 300.7857, 300.7101, 300.6415, 300.5792, 300.5227, 300.4717, 300.4256, 300.3842, 300.3471, 300.314, 300.2847, 300.2591, 300.2369, 300.2182, 300.2032, 300.1921, 300.1858, 300.1858],
    [301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.3, 301.1374, 300.9939, 300.8674, 300.756, 300.6578, 300.5712, 300.4949, 300.4276, 300.3683, 300.3159, 300.2697, 300.2288, 300.1928, 300.1609, 300.1328, 300.1079, 300.086, 300.0667, 300.0496, 300.0347, 300.0215, 300.01, 300.0001, 299.9915, 299.9842, 299.9781, 299.9733, 299.9698, 299.9678, 299.9678],
    [300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.3, 300.2331, 300.1785, 300.1335, 300.0964, 300.0654, 300.0396, 300.018, 299.9997, 299.9843, 299.9713, 299.9602, 299.9508, 299.9427, 299.9359, 299.93, 299.9249, 299.9206, 299.9169, 299.9137, 299.9109, 299.9086, 299.9065, 299.9048, 299.9034, 299.9022, 299.9012, 299.9004, 299.8998, 299.8995, 299.8995],
]
    
    initial_u = [[313.3534, 313.2928, 313.3008, 313.4002, 313.539, 313.6636, 313.7404, 313.7586, 318.4998, 318.4244, 318.3249, 318.2151, 318.1557, 318.1886, 318.325, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5, 320.5],
    [-0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 0.152, 0.1483, 0.145, 0.142, 0.1392, 0.1366, 0.1342, 0.1319, 0.1296, 0.1275, 0.1254, 0.1233, 0.1212, 0.1191, 0.1168, 0.1145, 0.112, 0.1093, 0.1063, 0.103, 0.0992, 0.095, 0.09, 0.0843, 0.0774, 0.069, 0.0585, 0.045, 0.0266, -0.0],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]]
    
    # Add zeros for the final segment of the horizon (combi4)
    initial_x = np.array([initial_x_i+[0]*15 for initial_x_i in initial_x])
    initial_u = np.array([initial_u_i+[0]*15 for initial_u_i in initial_u])
    
    opti.set_initial(u, initial_u)
    opti.set_initial(x, initial_x)
    
    # Solve the optimisation problem
    if PRINT: print("Solving the optimization problem...")
    start_time = time.time()
    success, err_message = True, ""
    try: sol = opti.solve()
    except Exception as e:
        success = False
        err_message = str(e).split()[-1]
        if PRINT: print(f"Failed to solve: {err_message}!")
    if PRINT: print("Done in {} seconds.".format(round(time.time()-start_time,1)))

    # Get optimal u=u_0*,...,u_N-1*
    u_optimal = sol.value(u) if success else np.nan

    # Get corresponding states x0,...,xN
    x_optimal = sol.value(x) if success else np.nan

    # Get the value of the objective at optimal
    obj_optimal = sol.value(obj) if success else 1e5

    # Return optimal sequence of u and x
    return u_optimal, x_optimal, obj_optimal, err_message
