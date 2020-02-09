"""
Helper functions and misc for objective function sobmodule
"""


class Coeff:
    """
    class for objective function coefficient. Not yet fully implemented and not fully used yet
    """
    def __init__(self, name, latex, default, min_val, max_val):
        """
        init
        :param name: string of name of coefficient
        :param latex: latex string of name of coefficient
        :param default: default value
        :param min_val: minimal value
        :param max_val: maximal value
        """
        self.name = name
        self.latex = latex
        self.default = default
        self.min = min_val
        self.max = max_val


def _round(num, n=2):
    """
    rounds if no decimal number for output string
    :param num: input number
    :return: rounded if num == x.0
    """
    if num % 1 == 0:
        return round(num)
    else:
        return round(num, n)