from pysb import Monomer, Parameter, Initial, Rule, Observable, Model
from pysb.simulator import ScipyOdeSimulator
from pylab import linspace, plot, xlabel, ylabel, show

# A simple model with a reversible binding rule
model = Model(name="t1", base=)

# Declare the monomers
L = Model.monomers('L', ['s'])
R = Monomer('R', ['s'])

# Declare the parameters
L_0 = Parameter('L_0', 100)
R_0 = Parameter('R_0', 200)
kf = Parameter('kf', 1e-3)
kr = Parameter('kr', 1e-3)

# Declare the initial conditions
Initial(L(s=None), L_0)
Initial(R(s=None), R_0)

# Declare the binding rule
Rule('L_binds_R', L(s=None) + R(s=None) | L(s=1) % R(s=1), kf, kr)

# Observe the complex
Observable('LR', L(s=1) % R(s=1))

if __name__ == '__main__':
    # Simulate the model through 40 seconds
    time = linspace(0, 40, 100)
    print("Simulating...")
    sim_result = ScipyOdeSimulator(model, time).run()

    # Plot the trajectory of LR
    plot(time, sim_result.observables['LR'])
    xlabel('Time (seconds)')
    ylabel('Amount of LR')
    show()