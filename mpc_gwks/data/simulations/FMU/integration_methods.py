import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Solve for real
def ode_func(t, x):
    
    delta_bu = 1
    m_buffer = 0.5
    cp = 4187
    T_HP_stor = 320
    
    Q_top1 = delta_bu * m_buffer * cp * (T_HP_stor - x)
    
    dxdt = 1/112/cp * Q_top1
    return dxdt

def get_real(x0, time_step):
    sol = solve_ivp(ode_func, (0, time_step), [x0], method='RK45')
    t = sol.t  # Time points
    y = sol.y[0]  # Solution values
    return y[-1]
    
def get_rk2(x0, time_step):
    sol = solve_ivp(ode_func, (0, time_step), [x0], method='RK23')
    t = sol.t  # Time points
    y = sol.y[0]  # Solution values
    return y[-1]

# Do real for 10 time steps
states_real = []
x0 = 300
for i in range(10):
    states_real.append(x0)
    x0 = get_real(x0,4*60)
    
# Do rk2 for 10 time steps
states_rk2 = []
x0 = 300
for i in range(10):
    states_rk2.append(x0)
    x0 = get_rk2(x0,4*60)
        
# Solve using euler
def get_euler(x0, time_step):

    delta_bu = 1
    m_buffer = 0.2
    cp = 4187
    T_HP_stor = 320
    
    Q_top1 = delta_bu * m_buffer * cp * (T_HP_stor - x0)
    
    x1 = x0 + time_step/(112*cp) * (Q_top1)
    return(x1)

# Do euler for 10 time steps
states_euler = []
x0 = 300
for i in range(10):
    states_euler.append(x0)
    x0 = get_euler(x0,4*60)

plt.plot(states_euler)
plt.scatter(range(len(states_euler)), states_euler, label='Euler')

plt.plot(states_rk2)
plt.scatter(range(len(states_rk2)), states_rk2, label='Runge-Kutta 23')

plt.plot(states_real)
plt.scatter(range(len(states_real)), states_real, label='Runge-Kutta 45')

plt.xlabel("Time steps (4 minutes each)")
plt.ylabel("Temperature [K]")

plt.xticks(list(range(0,10)))
plt.yticks(list(range(295,330,5)))
plt.ylim([299,321])

plt.legend()
plt.show()
