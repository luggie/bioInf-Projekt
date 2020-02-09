"""
Module Objective ObjectiveFunctions

Malte Korn

params: class for storing method parameter
algorithms: class for storing and adding new algorithms
bufferArray: array class for storing all precalculated information about all plot object such as points, vectors,
             and the like
"""


from .algorithms import GradientDescent, SimulatedAnnealing

# dictionary of algorithms which is used in main and
# which needs to extended if some new algorithm is implemented
Algorithms = {"Gradient Descent" : GradientDescent,
              "Simulated Annealing" : SimulatedAnnealing}