"""
Test for gui module
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
import unittest
import numpy as np

# modules from project
from objective_func import Polynomial, Sinus, Interpolated

# </editor-fold>
########### IMPORTS ###########


class TestObjectiveFunctions(unittest.TestCase):
    """
    Test class for objective functions inheriting from unittests
    """
    
    def test_poly(self):
        """
        polynomial testing
        """
        p = Polynomial([0,0,1])
        self.assertEqual(p(0), 0)
        self.assertEqual(p(5), 25)
        self.assertEqual(p(-3), 9)
        
        p = Polynomial([35,5,7])
        self.assertEqual(p(8.35), 564.8075)
        self.assertEqual(p(4.32), 187.23680000000002)
        self.assertEqual(p(-1.004), 37.036112)
        
    def test_sinus(self):
        """
        sinus testing
        """
        s = Sinus([4,8,3,5])
        self.assertEqual(s(0), 5.128960064478938)
        self.assertEqual(s(2*np.pi), 5.128960064478948)
        self.assertEqual(s(3.8), 3.929189525676769)

    def test_tangent_y(self):
        """
        tangent testing
        """
        for x in range(-10, 10):
            if x == 0: continue
            else:
                p = Polynomial([1,0,1])
                # x = -1
                y = p(x)
                learningrate = 0.1
                gradient = -learningrate * p(x, True)
                x_new = x + gradient
                y_arrow_end = p.tangent_y(x, y, x_new)
                self.assertLessEqual(y_arrow_end, y)


if __name__ == '__main__':
    unittest.main()
