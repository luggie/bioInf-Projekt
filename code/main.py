"""
Main call for NOViZ
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
import sys
from PyQt5 import QtWidgets

# modules from project
from gui import GuiFunctionParser
from optimization import GradientDescent, SimulatedAnnealing
from objective_functions import Polynomial, Sinus, Interpolated
from visualization import PlotCanvas

# </editor-fold>
########### IMPORTS ###########


class Main:
    """
    Main object class for initial call of program. Objects are passed on to GuiFunctionParser of gui module
    where functions recieved from user are processed and distributed
    """
    def __init__(self):
        """
        init
        """
        pass

    def calculate(self, objective_function, objective_function_params, method, method_params, startpoint):
        """
        Main Function. Initiates GUI and sends function,
        algorithm and method to according place
        :param objective_function: Objective function object
        :param objective_function_params: objective function parameter as list
        :param method: algorihm object
        :param method_params: algorithm parameter as list
        :param startpoint: start point as x coordinate
        :return: algorithm with everything set and buffer array computed
        """
        # objective_functions
        function = objective_function(objective_function_params)

        # optimization
        algorithm = method(function, method_params)
        algorithm.create_array(startpoint)

        return algorithm


if __name__ == "__main__":
    main = Main()
    plotcanvas = PlotCanvas()

    # gui
    app = QtWidgets.QApplication([])
    application = GuiFunctionParser(main, plotcanvas)
    application.show()
    sys.exit(app.exec())

