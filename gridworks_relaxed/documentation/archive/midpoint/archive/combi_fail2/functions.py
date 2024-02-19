import functions_00
import functions_01
import functions_10
import functions_11

'''
Get the combination [detla_ch, delta_bu] corresponding to the current time step
Split the horizon into four sections which each have there own combination
Typical situation: time step of 10min, horizon of N=12 (2 hours), splitting into four sections of 30min each.
'''
def get_function(id, u, x, a, real, approx, t, combi):

    N = combi['horizon']
    
    if t<N/4:                   current_combi = combi[f'combi1']
    if t>=N/4   and t<N/2:      current_combi = combi[f'combi2']
    if t>=N/2   and t<3*N/4:    current_combi = combi[f'combi3']
    if t>=3*N/4 and t<=N:       current_combi = combi[f'combi4']
        
    if current_combi == [0,0]: selected_function = functions_00.get_function(id, u, x, a, real, approx)
    if current_combi == [0,1]: selected_function = functions_01.get_function(id, u, x, a, real, approx)
    if current_combi == [1,0]: selected_function = functions_10.get_function(id, u, x, a, real, approx)
    if current_combi == [1,1]: selected_function = functions_11.get_function(id, u, x, a, real, approx)

    return selected_function
