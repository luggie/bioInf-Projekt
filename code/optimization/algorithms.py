"""
abstract class for algorithms (methods)
Set to be generic about newly added algoithms
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
from abc import ABC, abstractmethod
import numpy as np

# files from optimization
from optimization.bufferArray import BufferArray
from .params import Param

# </editor-fold>
########### IMPORTS ###########


def nextstep(y_old, y_new):
    """
    :param y_old: old y value
    :param y_new: new y value
    :return: False when threshold between y_old and y_new is reached. Return true otherwise
    """
    return (abs(y_old - y_new) > 0)


class Algorithm(ABC):
    """
    abstract base class that implements all functions and abstract functions that are
    necessary to add new algorithms
    """
    @abstractmethod
    def __init__(self, ObjectiveFunction):
        """
        init
        :param ObjectiveFunction: objective function on which the algorithm runs
        """
        self.ObjectiveFunction = ObjectiveFunction
        self.scatter = False
        self.scatter_colormapname = None
        self.scatter_min = None
        self.scatter_max = None

    @abstractmethod
    def create_array(self, startpoint):
        """
        abstract method that creates the full buffer array according to algorithm specific
        function and parameters
        :param startpoint: start point of calculation
        """
        pass

    def get_params_defaults(self):
        """
        creates list of param objects containing default values
        :returns: this list
        """
        params = self.get_params(self)
        params_list = []
        for param in params:
            params_list.append(param.default)
        return params_list

    def create_params_string(self, params):
        """
        creates string of params to be displayed
        :param params: algorithm parameters as list of param objects
        :return: this string
        """
        params_string = ""
        for param in params:
            params_string += param.name + ": " + str(param.default) + "\n"
        return params_string

    @abstractmethod
    def get_params(self):
        """
        :returns: usually a list of param objects of all the algorithms parameter
        """
        pass


class GradientDescent(Algorithm):
    """
    Gradient descent algorithm class (inheriting from which)
    """

    def __init__(self, ObjectiveFunction, params):
        """
        init a bufferArray
        :param ObjectiveFunction: chosen objective function
        :param params: list of parameters as
            those parameters are:
                - learning rate
                - max step
        """
        super(GradientDescent, self).__init__(ObjectiveFunction)
        self.ObjectiveFunction = ObjectiveFunction
        self.learningrate = params[0]
        self.max_steps = params[1]
        self.pseudocode = ['set iter$_{max}$, step = 0',
                           'x = set starting point',
                           'y = f(x)',
                           'while $(step < iter_{max}$)',
                           '$\quad x_{new} = x - step size \cdot  \delta f(x)$',
                           '$\quad$ x = $x_{new}$',
                           '$\quad$ y = f($x_{new}$)',
                           '$\quad step += 1$']
        self.buffer_array_length = int(self.max_steps * len(self.pseudocode))

    def create_array(self, startpoint):
        """
        create bufferArray of the results of the gradient descent algorithm
        :param startpoint: tuple of x, y coordinates of start point
        """
        self.array = BufferArray(self.buffer_array_length)
        next_step = True
        steps = 0
        x = startpoint
        y = self.ObjectiveFunction(x)
        x_lower_bound = -10000
        x_upper_bound = 10000

        # array.pushs in between are there to set current pseudo code line
        self.array.push(2, [[x, y]], None, None)
        while next_step and (steps < self.max_steps) and (x_lower_bound < x < x_upper_bound):
            self.array.push(3, [[x, y]], None, None)
            gradient = self.ObjectiveFunction(x, True)
            stepsize = -self.learningrate * gradient
            self.array.push(4, [[x, y]], None,
                            [[x, y, x - 1, y - gradient], [x, y, x + 1, y + gradient]])
            x_new = x + stepsize
            y_new = self.ObjectiveFunction(x_new)
            vector_y = self.ObjectiveFunction.tangent_y(x,y, x_new)
            self.array.push(6, [[x_new, y_new]], [[x, y, x_new-x, vector_y-y]],
                            [[x, y, x - 1, y - gradient], [x, y, x + 1, y + gradient]])
            steps += 1
            next_step = nextstep(y, y_new)

            x, y = x_new, y_new

    def get_params(self):
        """
        get gradient descent parameters
        :returns: those as list of param objects
        """
        lr = Param("Learning rate", "", 0.01, 0.001, 0.1)
        ms = Param("Max steps", "", 300, 1, 1000)
        return [lr, ms]


class SimulatedAnnealing(Algorithm):
    """
    Simulated Annealing algorithm class (inheriting from which)
    """

    def __init__(self, ObjectiveFunction, params):
        """
        init a bufferArray

        :param ObjectiveFunction: chosen objective function
        :param params: list of parameters as floats
            those parameters are:
            - max step
            - standard deviation
            - start temperature
            - temperature decrease rate
        """
        super(SimulatedAnnealing, self).__init__(ObjectiveFunction)
        self.ObjectiveFunction = ObjectiveFunction
        self.max_steps = params[0]
        self.standard_deviation = params[1]
        self.start_temperatur = params[2]
        self.temperatur_decreaserate = params[3]
        self.pseudocode = ['init: Temp.: $T$ and starting point: $x$',
                           'y = f(x)',
                           'step = 0',
                           'while ($T$ > 0) & $(step < iter_{max}$)',
                           '$\quad$ choose new point ($x_{new}$)',
                           '$\quad$ $y_{new}$ = $f(x_{new})$',
                           '$\quad$ if ($y_{new}$ < $y$)',
                           '$\quad\quad$ x = $x_{new}$, y = $y_{new}$',
                           '$\quad\quad$ set new starting point at (x, y)',
                           '$\quad$ else',
                           '$\quad\quad$ accept with prob. exp(-$\delta$/T)',
                           '$\quad T_{new} = T \cdot T$ decrease rate',
                           '$\quad$step += 1']
        self.scatter = True
        self.scatter_colormapname = 'plasma'
        self.scatter_min = 0
        self.scatter_max = self.start_temperatur
        self.buffer_array_length = int(self.max_steps * len(self.pseudocode))

    def create_array(self, startpoint):
        """
        create bufferArray of the results of the simulated annealing algorithm
        :param startpoint: tuple of x, y coordinates of start point
        """
        self.array = BufferArray(self.buffer_array_length)
        temperatur = self.start_temperatur
        step = 0
        x = startpoint
        y = self.ObjectiveFunction(x)
        self.array.push(0, [(x, y)], None, None, scatter=[(x, y, temperatur)])
        while (temperatur > 0) & (step < self.max_steps):  # temperatur > 0 -> macht das sinn?
            self.array.push(3, [(x, y)], None, None)
            random = np.random.normal(scale=self.standard_deviation)
            x_new = x + random
            y_new = self.ObjectiveFunction(x_new)
            self.array.push(5, [(x, y)], None, None, nextpoint=[[(x_new, y_new)], 'black'])
            self.array.push(6, [(x, y)], None, None, nextpoint=[[(x_new, y_new)], 'black'])
            if y_new < y:
                x = x_new
                y = y_new
                self.array.push(8, [(x, y)], None, None, nextpoint=[[(x_new, y_new)], 'green'])
            else: 
                self.array.push(9, [(x, y)], None, None, nextpoint=[[(x_new, y_new)], 'black'])
                p = np.exp(-(y_new - y) / temperatur)
                rand = np.random.random()
                if rand < p:
                    x = x_new
                    y = y_new
                    self.array.push(10, [(x, y)], None, None, nextpoint=[[(x_new, y_new)], 'green'])
                else:
                    self.array.push(10, [(x, y)], None, None, nextpoint=[[(x_new, y_new)], 'red'])
            self.array.push(12, [(x, y)], None, None, scatter=[(x, y, temperatur)])
            temperatur = temperatur * self.temperatur_decreaserate
            step += 1

    def get_params(self):
        """
        get simulated annealing parameters
        :returns: those as list of param objects
        """
        steps = Param("max step", "",100, 100, 10000)
        sdv = Param("std. deviation", "", 1.0, 0.001, 10.0)
        st = Param("Start temperature", "", 40, 0, 500)
        tdc = Param("temperature decr. rate", "", 0.8, 0.001, 10.0)
        return [steps, sdv, st, tdc]
