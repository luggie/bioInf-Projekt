"""
Module Objective ObjectiveFunctions

Sarah Gritzka sarah.gritzka@studium.uni-hamburg.de
Jonas Wember jonas.wember@studium.uni-hamburg.de

coeff: class for coefficients and misc
objective_func: classes for objective functions
objective_func_testing: test classes for objective functions
"""


from .objective_func import Polynomial, Sinus, Interpolated, LennardJonesPotential, TorsionPotential, BondAnglePotential, SimCrash

# dictionary of objective functions which is used in main and
# which needs to extended if some new objective function is implemented
ObjectiveFunctions = {"Polynomial" : Polynomial,
                      "Sinus" : Sinus,
                      "Interpolated" : Interpolated,
                      "Lennard Jones Pot." : LennardJonesPotential,
                      "Torsion Pot." : TorsionPotential,
                      "Bond Angle Pot." : BondAnglePotential,
                      "Sim. Ann. Nemesis" : SimCrash}
