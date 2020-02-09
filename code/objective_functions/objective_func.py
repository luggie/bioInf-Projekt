#!/usr/bin/env python3

"""
abstract class for energy landscape functions
Set to be generic about newly added functions
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
import pyclbr
from abc import ABC, abstractmethod
from operator import itemgetter
import numpy as np
import re
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# files from objective functions
from .coeff import Coeff, _round

# </editor-fold>
########### IMPORTS ###########


class ObjectiveFunction(ABC):

    @abstractmethod
    def __init__(self, coeff):
        """
        the initializer for the abstract base class for all objective functions
        """

        self.coeff = coeff

    def tangent_y(self, x, y, x_new):
        """
        calculate position of arrow end
        :param x: x coordinate of arrow start point
        :param y: y coordinate of arrow start point
        :param x_new: x coordinate of arrow end point
        :return: y coordinate of arrow end point
        """
        slope = self.__call__(x, True)
        intercept = y - slope * x
        return slope * x_new + intercept

    # TODO: under construction
    # def AddFunctions(self, x, other, derivative):
    #     """
    #     Function adds two or more types of objective functions and returns value
    #     :param x: x value
    #     :param other: other function(s)
    #     :param derivative: bool
    #     :return: return 'y' value
    #     """
    #
    #     if derivative:
    #         new_value = self.__call__(x, True)
    #         for func in other:
    #             new_value = new_value + func.__call__(x, True)
    #         return new_value
    #     else:
    #         new_value = self.__call__(x)
    #         for func in other:
    #             new_value = new_value + func.__call__(x)
    #         return new_value

    # TODO: under construction
    # def MultiplyFunctions(self, x, other):
    #     """
    #     Function multiplies two or more types of objective functions and returns value
    #     :param x: x value
    #     :param other: other function(s)
    #     :return: return 'y' value
    #     """
    #
    #     if derivative:
    #         new_value = self.__call__(x, True)
    #         for i in range(0, len(other)):
    #             new_value + func.__call__(x, True)
    #         return new_value
    #     else:
    #         new_value = self.__call__(x)
    #         for func in other:
    #             new_value * func.__call__(x)
    #     return new_value

    @abstractmethod
    def get_coeffs(self, num_coeffs):
        """
        abstract method that get current function coefficients
        :param num_coeffs: number of coefficients
        """
        pass

    @abstractmethod
    def create_formula_string(self, coeffs):
        """
        abstract method that creates a string for the forumula output label
        :param coeffs function coefficients:
        """
        pass

    def get_coeffs_defaults(self):
        """
        sets default parametrs from coeff objects
        """
        coeffs = self.get_coeffs(self)
        coeffs_list = []
        for coeff in coeffs:
            coeffs_list.append(coeff.default)
        return coeffs_list

    def get_axes_parameters(self, coeffs):
        """
        get preferred x/y lims for input coefficients
        :param coeffs: function coefficients
        """
        pass


class Polynomial(ObjectiveFunction):
    """
    class for polynomial objective functions inheriting from abstract base class
    """

    def __init__(self, coeff):
        """
        initializer for a polynomial function
        :param coeff: is a list of coefficients
        """
        super(Polynomial, self).__init__(coeff)
        self.coeff = coeff

    # makes a more intuitive programming possible with f(x)
    def __call__(self, x, derivative=False):
        """
        makes it possible to call a function at a more mathematical
        approach e.g. f(x)
        :param x: is a list of coefficients
        :param derivative: bool which determines if the derivative of a function should be used (default False)
        """
        if derivative:
            res = 0
            for index, c in enumerate(self.coeff):
                res += index * c * x ** (index - 1)
            return res
        else:
            res = 0
            for index, c in enumerate(self.coeff):
                # print("here", x, res)
                res += c * x ** index
            return res

    def __str__(self):
        """
        print representation of polynomial objective function
        """
        return "Polynomial"

    def get_coeffs(self, num_coeffs=3):
        """
        get current function coefficients
        :param num_coeffs: number of coefficients
        :return list of coeff objects
        """
        constant = Coeff("constant", "$Constant$", 1, -10, 10)
        coeffs = [constant]
        for i in range(1, num_coeffs):
            if i == 1:
                coeffs.append(Coeff("x", "$x$", 1, -10, 10))
            else:
                coeffs.append(
                    Coeff("x^" + str(i), "$x^{" + str(i) + "}$", 1, -10, 10))
        return coeffs

    def create_formula_string(self, coeffs):
        """
        creates a string for the forumula output label
        :param coeffs: function coefficients
        :return formula string to be used by mathtex_to_qpixmap
        """
        self.coeff_string = ""
        coeff_count = len(coeffs) - 1
        for coeff in reversed(coeffs[1:len(coeffs)]):
            if coeff:
                if coeff == 1:
                    if coeff_count == 1:
                        self.coeff_string += "x + "
                    else:
                        self.coeff_string += "x^" + str(coeff_count) + " + "
                else:
                    if coeff_count == 1:
                        self.coeff_string += str(_round(coeff)) + "x + "
                    else:
                        self.coeff_string += str(_round(coeff)) + "x^" + str(
                            coeff_count) + " + "
            coeff_count -= 1
        if coeffs[0]:
            self.coeff_string += " " + str(_round(coeffs[0]))
        else:
            self.coeff_string = self.coeff_string[:-3]
        self.coeff_string = re.sub('\+\s+-', '-', self.coeff_string)
        self.coeff_string = re.sub('-1x', '-x', self.coeff_string)

        self.formula_string = "$f(x) = " + self.coeff_string + "$"

        return self.formula_string

    def get_axes_parameters(self):
        """
        set x/y lims for input coefficients and
        :returns: them
        """
        y_min = self.coeff[0]
        y_max = 10
        x_min = -5
        x_max = 5
        return y_min, y_max, x_min, x_max


class Sinus(ObjectiveFunction):
    """
    class for sinus objective functions inheriting from abstract base class
    """

    def __init__(self, coeff):
        """
        initializer for a sinus function
        :param coeff: list of sinus coefficients
        """
        super(Sinus, self).__init__(coeff)
        self.coeff = coeff

    def __call__(self, x, derivative=False):
        """
        makes it possible to call a function at a more mathematical
        approach e.g. f(x)
        :param x: is a list of coefficients
        :param derivative: bool which determines if the derivative of a function should be used (default False)
        """
        if derivative:
            return np.cos(x * self.coeff[3] + self.coeff[2]) * self.coeff[1] * \
                   self.coeff[3]
        else:
            return np.sin(x * self.coeff[3] + self.coeff[2]) * self.coeff[1] + \
                   self.coeff[0]

    def __str__(self):
        """
        print representation of sinus objective function
        """
        return "Sinus"

    def get_coeffs(self, num_coeffs=4):
        """
        get current function coefficients
        :param num_coeffs: number of coefficients
        :return list of coeff objects
        """
        constant = Coeff("constant", "$Constant$", 1, -10, 10)
        amplitude = Coeff("amplitude", "$Amplitude$", 1, -10, 10)
        phase = Coeff("phase", "$Phase$", 1, -10, 10)
        period = Coeff("Periode", "$Periode$", 1, -10, 10)
        return [constant, amplitude, phase, period]

    def create_formula_string(self, coeffs):
        """
        creates a string for the forumula output label
        like this:

        a        *sin(b        *x+c        )+d          with function_coeffs in order of:
        function_coeffs[1]*sin(function_coeffs[3]*x+function_coeffs[2])+function_coeffs[0]

        :param coeffs: function coefficients
        :return formula string to be used by mathtex_to_qpixmap
        """

        a = str(_round(coeffs[1]))
        b = str(_round(coeffs[3]))
        c = str(_round(coeffs[2]))
        d = str(_round(coeffs[0]))

        self.coeff_string = a + "sin(" + b + "x + " + c + ") + " + d

        self.coeff_string = re.sub('^1sin', 'sin', self.coeff_string)
        self.coeff_string = re.sub('^0sin\(.*\)', '', self.coeff_string)
        self.coeff_string = re.sub('\(1x', '(x', self.coeff_string)
        self.coeff_string = re.sub('\(0x', '(', self.coeff_string)
        self.coeff_string = re.sub(' \+ 0\)', ')', self.coeff_string)
        self.coeff_string = re.sub(' \+ 0(?!\.)', '', self.coeff_string)
        self.coeff_string = re.sub('^\+', '', self.coeff_string)
        self.coeff_string = re.sub('\+ -', '-', self.coeff_string)
        self.coeff_string = re.sub('\(-1x', '(-x', self.coeff_string)
        self.coeff_string = re.sub('^-1sin', '-sin', self.coeff_string)
        self.coeff_string = re.sub('0x [\+|-] (\d+)', ' \1', self.coeff_string)

        self.formula_string = "$f(x) = " + self.coeff_string + "$"

        return self.formula_string

    def get_axes_parameters(self):
        """
        calculates minimum and maximum settings for x and y axes
        according to function parameters
        :return: 4 fold tuple of float numbers
        """
        y_min = self.coeff[0] - self.coeff[1] - self.coeff[1] / 2
        y_max = self.coeff[0] + self.coeff[1] + self.coeff[1] / 2
        x_min = -1
        x_max = 2 * 1 / self.coeff[3] * np.pi
        if y_min > y_max:
            y_min, y_max = y_max, y_min  # das ist python magie <3_
        if x_min > x_max:
            x_min, x_max, = x_max, x_min
        return y_min, y_max, x_min, x_max


class Interpolated(ObjectiveFunction):
    """
    Interpolated function from scipy which draws a cubis spline though some points
    that are set by user input
    """

    def __init__(self, coeff):
        """
        initializer for a sinus function
        :param coeff: list of user input points
        """
        super(Interpolated, self).__init__(coeff)

        self.coeff = coeff

    def __call__(self, x, derivative=False):
        """
        makes it possible to call a function at a more mathematical
        approach e.g. f(x)
        :param x: is a list of coefficients
        :param derivative: bool which determines if the derivative of a function should be used (default False)
        """
        x_points = []
        y_points = []
        self.coeff.sort(key=itemgetter(0))
        for val in enumerate(self.coeff):
            x_points = np.append(x_points, val[1][0])
            y_points = np.append(y_points, val[1][1])
        if derivative:
            f = CubicSpline(x_points, y_points).derivative()
            return f(x)
        else:
            f = CubicSpline(x_points, y_points)
            return f(x)

    def __str__(self):
        """
        print representation of interpolated objective function
        """
        return "Interpolated"

    def get_coeffs(self, num_coeffs=0):
        """
        get current function coefficients
        isn't needed in interpolated objective functions
        :param num_coeffs: number of coefficients
        :return list of dummy list of dummy coeff objects
        """
        return [Coeff("Dummy", "$Dummy$", 0, 0, 0)]

    def create_formula_string(self, coeffs):
        """
        creates formula string but isn't needed in interpolated objective functions
        :param coeffs: list of coeff objects
        :return: empty dummy string
        """
        return ""

    def get_axes_parameters(self):
        """
        calculates minimum and maximum settings for x and y axes
        according to function parameters
        :return: 4 fold tuple of float numbers
        """
        x_min = self.coeff[0][0] - 1
        x_max = self.coeff[-1][0] + 1
        y_min = min(self.coeff, key=itemgetter(1))[1] - 1
        y_max = max(self.coeff, key=itemgetter(1))[1] + 1
        return y_min, y_max, x_min, x_max


class SimCrash(ObjectiveFunction):
    """
    class for preset objective functions that makes simulated annealing have a hard time
    """

    def __init__(self, coeff):
        """
        initializer for a sim crasj function
        :param coeff: is a list of coefficients
        """
        self.coeff = coeff

    # makes a more intuitive programming possible with f(x)
    def __call__(self, x, derivative=False):
        """
        makes it possible to call a function at a more mathematical
        approach e.g. f(x)
        :param x: is a list of coefficients (not needed here)
        :param derivative: bool which determines if the derivative of a function should be used (default False)
        """
        if derivative:
            # return -(np.exp(12.5*(x-1)**2) - 0.5 * (np.exp(-(x+1)**2/18)))
            return np.exp(-1/18 * (x + 1)**2)*(0.0555556*x + 0.0555556) + 100. * np.exp(-50. *(x - 1)**2)*(x - 1)
            # return ((x + 1) * (np.exp((-(x + 1) ** 2))) / 18) / 18 + 100 * (x - 1) * np.exp(-50 * (x - 1) ** 2)
        else:
            return -np.exp((-(x - 1) ** 2) / (2 * 0.1 ** 2)) - 0.5 * np.exp((-(x + 1) ** 2) / (2 * 3 ** 2))

    def create_formula_string(self, coeffs):
        """
        :param coeffs: not needed in sim crash objective function
        :returns: preset function formula in latex notation
        """
        return "$f(x)=-e^{-\dfrac{(x-2)^2}{2*0.1^2}}-e^{-\dfrac{(x+2)^2}{2*3^2}}$"

    def get_coeffs(self, num_coeffs=0):
        """
        get current function coefficients
        isn't needed in sim crash objective function
        :param num_coeffs: number of coefficients
        :return list of dummy list of dummy coeff objects
        """
        return [Coeff("Dummy", "$Dummy$", 0, 0, 0)]

    def get_axes_parameters(self):
        """
        calculates minimum and maximum settings for x and y axes
        according to function parameters
        :return: 4 fold tuple of float numbers
        """
        y_min = -2
        y_max = 2
        x_min = -5
        x_max = 5
        return y_min, y_max, x_min, x_max


class LennardJonesPotential(ObjectiveFunction):
    """
    class for lennard jones potential objective functions inheriting from abstract base class
    """

    def __init__(self, coeff):
        """
        initializer for a Lennard-Jones function
        :param coeff: list of coefficients
        """

        self.coeff = coeff

    def __call__(self, x, derivative=False):
        """
        makes it possible to call a function at a more mathematical
        approach e.g. f(x)
        :param x: is a list of coefficients (not needed here)
        :param derivative: bool which determines if the derivative of a function should be used (default False)
        """
        if derivative:
            return 24 * self.coeff[0] * self.coeff[1] ** 6 * \
                   (x ** 6 - 2 * self.coeff[1] ** 6) / x ** 13
        else:
            return 4 * self.coeff[0] * ((self.coeff[1] ** 12 / (x ** 12)) - (
                        self.coeff[1] ** 6 / (x ** 6)))

    def __str__(self):
        """
        Print representation of lennard jones potential function
        :returns: this
        """
        return "Lennard Jones Potential"

    def create_formula_string(self, coeffs):
        """
        :param coeffs: list of coeff objects
        :returns: string of function formula in latex notation
        """
        coeff1 = str(_round(float(coeffs[0]) * 4))
        self.formula_string = "$f(x)= " + coeff1 + "\dfrac{" + str(
            coeffs[1]) + "^{12}}{x^{12}}-\dfrac{" + str(
            coeffs[1]) + "^6}{x^6}$"
        return self.formula_string

    def get_coeffs(self, num_coeffs=2):
        """
        get current function coefficients
        :param num_coeffs: number of coefficients
        :return list of coeff objects
        """
        epsilon = Coeff("epsilon", "$\epsilon$", 6, -10, 10)
        sigma = Coeff("sigma", "$\sigma$", 3.5, -10, 10)
        return [epsilon, sigma]

    def get_axes_parameters(self):
        """
        calculates minimum and maximum settings for x and y axes
        according to function parameters
        :return: 4 fold tuple of float numbers
        """
        y_min = -self.coeff[0] - 1
        y_max = self.coeff[0]
        x_min = 0
        x_max = self.coeff[1] * 2
        return y_min, y_max, x_min, x_max


class TorsionPotential(ObjectiveFunction):
    """
    class for lennard jones potential objective functions inheriting from abstract base class
    """

    def __init__(self, coeff):
        """
        init
        :param coeff: list of coeff objects
        (theta_0 : float : optimal angle for certain atom combination (C-C-C, C-N-C,....)
        k : float : bond strength constant
        """
        super(TorsionPotential, self).__init__(coeff)
        self.coeff = coeff

    def __call__(self, x, derivative=False):
        """
        makes it possible to call a function at a more mathematical
        approach e.g. f(x)
        :param x: is a list of coefficients (not needed here)
        :param derivative: bool which determines if the derivative of a function should be used (default False)
        """
        if derivative:
            return -self.coeff[1] * (np.cos(x) - np.cos(self.coeff[0])) * np.sin(x)
        else:
            return self.coeff[1] / 2 * (np.cos(x) - np.cos(self.coeff[0])) ** 2

    def __str__(self):
        """
        :returns: torsian angle potential objective function print representation
        """
        return "Torsion Potential"

    def get_coeffs(self, num_coeffs=2):
        """
        get current function coefficients
        :param num_coeffs: number of coefficients
        :return list of coeff objects
        """
        epsilon = Coeff("theta0", "$\Theta_0$", np.pi * 3 / 4, -10, 10)
        sigma = Coeff("k", "$k$", 2.7, -10, 10)
        return [epsilon, sigma]

    def create_formula_string(self, coeffs):
        """
        :param coeffs: list of coeff objects
        :returns: string of function formula in latex notation
        """
        self.formula_string = "$f(x)=\dfrac{" + str(_round(coeffs[1])) + \
                              "}{2}( cos(x) - cos(" + str(_round(coeffs[0])) + "))^2$"
        return self.formula_string

    def get_axes_parameters(self):
        """
        calculates minimum and maximum settings for x and y axes
        according to function parameters
        :return: 4 fold tuple of float numbers
        """
        y_min = -self.coeff[1] * 2
        y_max = self.coeff[1] * 2
        x_min = -1
        x_max = 10
        if y_min > y_max:
            y_min, y_max = y_max, y_min
        return y_min, y_max, x_min, x_max


class BondAnglePotential(ObjectiveFunction):
    """
    class for bond angle potential objective functions inheriting from abstract base class
    """

    def __init__(self, coeff):
        """
        init
        :param coeff: list of coeff objects
        (theta_0 : float : optimal angle for certain atom combination (C-C-C, C-N-C,....)
        k : float : bond strength constant
        """
        super(BondAnglePotential, self).__init__(coeff)
        self.coeff = coeff

    def __call__(self, x, derivative=False):
        """
        makes it possible to call a function at a more mathematical
        approach e.g. f(x)
        :param x: is a list of coefficients (not needed here)
        :param derivative: bool which determines if the derivative of a function should be used (default False)
        """
        if derivative:
            return self.coeff[1] * (x - self.coeff[0])
        else:
            return self.coeff[1] / 2 * (x - self.coeff[0]) ** 2

    def __str__(self):
        """
        :returns: bond angle potential objective function print representation
        """
        return "Bond Angle Potential"

    def get_coeffs(self, num_coeffs=2):
        """
        get current function coefficients
        :param num_coeffs: number of coefficients
        :return list of coeff objects
        """
        epsilon = Coeff("theta0", "$\Theta_0$", np.pi * 3 / 4, -10, 10)
        sigma = Coeff("k", "$k$", 2.7, -10, 10)
        return [epsilon, sigma]

    def create_formula_string(self, coeffs):
        """
        :param coeffs: list of coeff objects
        :returns: string of function formula in latex notation
        """
        self.formula_string = "$f(x)=\dfrac{" + str(_round(coeffs[1])) + \
                              "}{2}( x - " + str(_round(coeffs[0])) + ")^2$"
        return self.formula_string

    def get_axes_parameters(self):
        """
        calculates minimum and maximum settings for x and y axes
        according to function parameters
        :return: 4 fold tuple of float numbers
        """
        y_min = -1
        y_max = self.coeff[1] * 2
        x_min = -1
        x_max = 5
        if y_min > y_max:
            y_min, y_max = y_max, y_min
        return y_min, y_max, x_min, x_max

# TODO: Under construction
#class Torda(ObjectiveFunction):
#
#    def __init__(self, coeff):
#        super(Torda, self).__init__(coeff)
#        """initializer for a interpolated function
#
#        Keyword Arguments:
#        coeff: is a list of coordinates to be interpolated
#        """
#        self.coeff = [(0.24807597838545803, 9.4836870446626591),
#                      (0.72294088750613916, 3.5761799176433322),
#                      (1.2551170787620753, 1.0262907823883411),
#                      (1.86097920419191, 2.0557491289198593),
#                      (2.3767807434092014, 1.1371555273994276),
#                      (2.9007696086458155, 1.0262907823883411),
#                      (3.4984444080563279, 1.9132087424770341),
#                      (3.7604388406746341, 1.152993348115297),
#                      (4.4399869002783685, 1.2163446309787753),
#                      (5.1195349598821025, 7.266392144440931),
#                      (5.6271491730800722, 8.7393094710167958),
#                      (6.5277550352055016, 2.2616407982261633),
#                      (8.4763386278041573, 6.8070953436807153),
#                      (7.2482397249058437, 0.13937282229964754)]
#
#    def __call__(self, x, derivative=False):
#        """makes it possible to call a function at a more mathematical
#        approach e.g. f(x)
#
#        Keyword arguments:
#        x: is a list of coefficients
#        derivative: bool which determines if the derivative of a function
#        should be used (default False)
#        """
#        x_points = []
#        y_points = []
#        self.coeff.sort(key=itemgetter(0))
#        for val in enumerate(self.coeff):
#            x_points = np.append(x_points, val[1][0])
#            y_points = np.append(y_points, val[1][1])
#        if derivative:
#            f = CubicSpline(x_points, y_points).derivative()
#            return f(x)
#        else:
#            f = CubicSpline(x_points, y_points)
#            return f(x)
#
#    def __str__(self):
#        return "Torda"
#
#    def get_coeffs(self, num_coeffs=0):
#        return []
#
#    def create_formula_string(self, coeffs):
#        return ""
#
#    def get_axes_parameters(self):
#        """
#        calculates minimum and maximum settings for x and y axes
#        according to function parameters
#        :return: tuple of size 4 of float numbers
#        """
#        x_min = self.coeff[0][0] - 1
#        x_max = self.coeff[-1][0] + 1
#        y_min = min(self.coeff, key=itemgetter(1))[1] - 1
#        y_max = max(self.coeff, key=itemgetter(1))[1] + 1
#        return y_min, y_max, x_min, x_max


if __name__ == "__main__":
    p = SimCrash(0)
    x = np.linspace(-10, 5, 100, endpoint=True)
    plt.axis([-10, 5, -2, 1.5])
    print(p(3.9, True))
    plt.plot(x, p(x), "b")
    plt.plot(x, p(x, True), "g--")
    plt.arrow(4, p(4), 1, p(4, True), width=0.01, head_width=0.1, head_length=1,
              length_includes_head=True)
    plt.show()
