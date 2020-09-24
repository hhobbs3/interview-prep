from __future__ import print_function
from pysb.simulator import ScipyOdeSimulator
from .PySB_tutorial import model

t = [0, 10, 20, 30, 40, 50, 60]
simulator = ScipyOdeSimulator(model, tspan=t)
simresult = simulator.run()
print(simresult.species)