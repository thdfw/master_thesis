import functions_00
import functions_01
import functions_10
import functions_11

def get_function(id, u, x, a, real, approx, t, combi):

    # Get the combination [detla_ch,delta_bu]
    # which was requested for at time step t (t=0,1,...,N-1)
    # where typically N=4 (2 hours forward for 30min time step)
    current_combi = combi[f'timestep{t}']
        
    if current_combi == [0,0]: selected_function = functions_00.get_function(id, u, x, a, real, approx)
    if current_combi == [0,1]: selected_function = functions_01.get_function(id, u, x, a, real, approx)
    if current_combi == [1,0]: selected_function = functions_10.get_function(id, u, x, a, real, approx)
    if current_combi == [1,1]: selected_function = functions_11.get_function(id, u, x, a, real, approx)

    return selected_function
