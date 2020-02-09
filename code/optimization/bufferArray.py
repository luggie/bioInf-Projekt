"""
Buffer Array class.
Contains all plot relevant entities and is stored when objective function, algorithm and depending parameters as well
as a start point are set and button 'calculate' is pressed.
See "Arrayentry" for more information
"""


########### IMPORTS ###########
#<editor-fold desc="Open">

# packages
import collections

#</editor-fold>
########### IMPORTS ###########


Arrayentry = collections.namedtuple('Arrayentry',
                                    ('pseudocodeline',
                                     'points',
                                     'vectors',
                                     'lines',
                                     'scatterpoints_position',
                                     'nextpoint',
                                     'lowest_point'))


class BufferArray:    
    """
    Creats Array with a capacity to store pseudocodeline, points, vectors,
    lines as named tuple.
    """
    def __init__(self, capacity):
        """
        init
        :param capacity: size of buffer array
        """
        self.capacity = capacity
        self.memory = [None for _ in range(capacity)]
        self.scatterpoint_array = []
        self.next_empty_postiton = 0
        self.current_step = 0
        self.minimum = 0

    def __getitem__(self, key):
        """
        :param key: element index which is requested
        :returns: key-th element in buffer array or raises IndexError if not possible
        """
        try:
            return self.memory[key]
        except IndexError as error:
            print('index out of range', error)

    def __call__(self, offset=0):
        """
        return current step in buffer array as a function type
        :param offset: can be used to check on any entry e.x. self.memory(step-1) and
        :returns this
        """
        return self.memory[self.current_step + offset]

    def __iter__(self):
        """
        makes buffer array iterable
        :returns: iter
        """
        return iter(self.memory)

    def __str__(self):
        """
        generate string of the Array; empty positions are not note
        :returns this
        """
        string = str(self.memory).replace("), Arrayentry(", "\n")
        string = string.strip(", None]").strip("), None")
        string = string.strip(", None").strip("[Arrayentry(")
        return string

    def __len__(self):
        """
        :returns: length of actually filled buffer array
        """
        return self.next_empty_postiton

    def push(self, pseudocodeline, points, vectors, lines, scatter=None, nextpoint=None):
        """
        write a named tuple(pseudocodeline, points,v ectors, lines) to the next empty Position
        :param pseudocodeline: position of pseudo code line
        :param points: list of tuples of x, y coordinates of points
        :param vectors: vectors objects of the form: ([(x,y,dx,dy), ...])
        :param lines: line objects of the form ([(start_x,start_y,end_x,end_y), ...])
        """
        try:
            if scatter:
                for point in scatter:
                    self.scatterpoint_array.append(point)
            smaller, lowest_point = self._smaller(points, self.minimum)
            if smaller:
                self.minimum = self.next_empty_postiton
            self.memory[self.next_empty_postiton] = Arrayentry(pseudocodeline, points,
                         vectors, lines, len(self.scatterpoint_array), nextpoint, lowest_point)
            self.next_empty_postiton = self.next_empty_postiton + 1
        except IndexError as error:
            print('<array full>', error)

    def set_last_position(self):
        """
        sets buffer array position to last filled position
        """
        self.current_step = self.next_empty_postiton - 1

    def set_first_position(self):
        """
        sets buffer array position to first position
        """
        self.current_step = 0
    
    def last_position(self):
        """
        :returns last available position
        """
        return self.current_step == self.next_empty_postiton - 1

    def get_minimum(self):
        """
        :returns: minimal value
        """
        return self.minimum

    def _smaller(self, points, comparing_pos):
        """
        :param points: list of points, consisting of x, y values
        :param comparing_pos: x, y coordinates of comparing point
        :returns True if the smallest y value at memory[pos].points is smaller then the
        the smallest y value at memory[comparing_pos].points
        """
        if self.memory[comparing_pos]:
            pos_smallest = float("inf")
            comp_pos_smallest = float("inf")
            for point in points:
                if point[1] < pos_smallest:
                    pos_smallest = point
            for point in self.memory[comparing_pos].points:
                if point[1] < comp_pos_smallest:
                    comp_pos_smallest = point
            smaller = pos_smallest[1] < comp_pos_smallest[1]
            smallest_value = pos_smallest if smaller else comp_pos_smallest
            return smaller, [smallest_value]
        return True, None