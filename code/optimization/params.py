"""
Helper functions and misc for algorithm sobmodule
"""


class Param:
    """
    class for algorithm parameters. Not yet fully implemented and not fully used yet
    """
    def __init__(self, name, latex, default, min_val, max_val):
        """
        init
        :param name: string of name of parametr
        :param latex: latex string of name of parameter
        :param default: default value
        :param min_val: minimal value
        :param max_val: maximal value
        """
        self.name = name
        self.latex = latex
        self.default = default
        self.min = min_val
        self.max = max_val
