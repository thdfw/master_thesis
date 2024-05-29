from functions import generic

parameters_HPTES = { 
    'horizon': 24,

    'elec_costs': [7.92, 6.63, 6.31, 6.79, 8.01, 11.58, 19.38, 21.59, 11.08, 4.49, 1.52, 0.74, 
                   0.42, 0.71, 0.97, 2.45, 3.79, 9.56, 20.51, 28.26, 23.49, 18.42, 13.23, 10.17],
    
    'load': {'type': 'hourly', 
             'value': [5.91, 5.77, 5.67, 5.77, 5.71, 6.06, 6.34, 6.34, 6.01, 5.77, 5.05, 5.05, 
                       4.91, 4.91, 4.91, 4.91, 5.05, 5.1, 4.91, 4.91, 4.91, 4.91, 4.98, 4.91]},

    'control': {'type': 'range',
                'max': [12]*24,
                'min': [6]*24},
    
    'constraints': {'storage_capacity': True,
                    'max_storage': 30,
                    'initial_soc': 0,
                    'cheaper_hours': True,
                    'quiet_hours': False
                    },
}

control = generic(parameters_HPTES)
print(f"\nThe control sequence is:\n{control}\n")