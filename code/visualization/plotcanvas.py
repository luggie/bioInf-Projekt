"""
Plotcanvas submodule.

Processes initiation, alteration and reset of matplotlib canvas object,
instantiated in gui.function_parser
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
import numpy as np
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import QEventLoop, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# files from visualization
from .navigation import zoom, drag, drop, move

# </editor-fold>
########### IMPORTS ###########


class PlotCanvas(FigureCanvas):
    """
    Plotcanvas class, inherits from matplotlib's FigureCanvas class
    and extends it with specific methods and attributes.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        init
        :param parent: parent object of plotcanvas (which causes some error for save fig)
        :param width: width of canvas in inches
        :param height: height of canvas in inches
        :param dpi: dots per inch. resolution density
        """

        self.parent = parent
        self.plot_width = width
        self.plot_height = height
        self.plot_dpi = dpi

        # Algorithm buffer array (self.Algorithm.array)
        self.algorithm = None

        # init of matplotlib figure, axes and canvas
        self._init_matplotlib_objects()

        # init drag'n'drop and zoom
        self._init_dragndrop()

        # init spinbox_currentposition
        self.spinbox_currentposition = None

        # init colorbar
        self.colorbar = None

        # save plot and plot objects
        self._plot_inits()

        # more inits
        self._additional_inits()

    def _additional_inits(self):
        """
        misc inits
        """
        # interpolated points
        self.points_for_interpolation = []
        # sleep time for play animation
        self.sleep_time = 500
        # tracing
        self.tracing_switch = False
        self.current_points = None
        self.zoom = 5
        # xy coords
        self.current_x = 0.0
        self.current_y = 0.0
        # start point
        self.clicked_start_points = []
        self.start_point_click = None

    def set_algorithm(self, Algorithm):
        """
        :param Algorithm: Algorithm object from optimization.algorithms
        """
        self.algorithm = Algorithm

###########################################
#  init plotcanvas objects and functions  #
###########################################

    def _plot_inits(self):
        """
        plot (not figure or plot canvas) related inits
        """
        self.curve = self._init_curve()
        self.points = self._init_points()
        self.scatter_points = None  # init needed in Algorithm because of colormap scale (self._init_scatter_points())
        self.vectors = []
        self.lines = []
        self.lowest_point = self._init_lowestpoint()
        self.nextpoint = self._init_nextpoint()

    def _init_dragndrop(self):
        """
        initialisation parameters for drag'n'drop functions
        """
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.fig.canvas.mpl_connect('button_press_event', lambda event: drag(self, event))
        self.fig.canvas.mpl_connect('button_release_event', lambda event: drop(self))
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: move(self, event))

        # init mouse wheel zoom
        self.fig.canvas.mpl_connect('scroll_event', lambda event: zoom(self, event))

    def _init_matplotlib_objects(self):
        """
        primary initialisation of matplotlib canvas objects
        """
        self.fig = Figure(figsize=(self.plot_width, self.plot_height), dpi=self.plot_dpi)
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111, facecolor=(0.94, 0.94, 0.94))  # bg color of plot frame
        self.fig.set_facecolor((0.94, 0.94, 0.94))  # frame color

        # Superclass FigureCanvas from matplotlib is called.
        FigureCanvas.__init__(self, self.fig)
        self.setParent(self.parent)  # set parenthood

        # size policy
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        # disable display coordinates
        self.axes.format_coord = lambda x, y: ""

        # set axes and grid
        self.axes.cla()
        self.axes.set_xlim(-5, 5)
        self.axes.set_ylim(0, 10)
        self.axes.grid(color='gray', alpha=0.5, linestyle='dashed', linewidth=0.5)

        # set origin axes
        self.axes.spines['left'].set_position('zero')  # x
        self.axes.spines['right'].set_color('none')
        self.axes.yaxis.tick_left()
        self.axes.spines['bottom'].set_position('zero')  # y
        self.axes.spines['top'].set_color('none')

        # no gap between axes and figure
        self.fig.tight_layout()

    def _init_curve(self):
        """
        :return: empty function curve
        """
        curve = self.axes.plot([], [])[0]
        return curve

    def _init_points(self):
        """
        :return: empty set of points
        """
        return self.axes.plot([], [], color='#339966', marker='o', linestyle='dashed', markersize=5)[0]

    def _init_scatter_points(self):
        if self.algorithm.scatter:
            colormap_name = self.algorithm.scatter_colormapname
            minimum = self.algorithm.scatter_min
            maximum = self.algorithm.scatter_max
            self.scatter_points = self.axes.scatter([0, 0], [0, 0], marker='o',
                                                    c=[minimum, maximum], cmap=plt.get_cmap(colormap_name))

            if self.colorbar is None:
                self.colorbar = self.fig.colorbar(self.scatter_points)
            else:
                self.fig.get_axes()[1].set_visible(False)

    def _init_nextpoint(self):
        """
        :return: empty set of points
        """
        return self.axes.plot([], [], color='black', marker='x', linestyle='dashed', markersize=10)[0]

    def _init_lowestpoint(self):
        """
        :return: empty set of points
        """
        return self.axes.plot([], [], color='c', marker='*', linestyle='dashed', markersize=6)[0]

#############################
# update plotcanvas objects #
#############################

    def show_plot(self):
        """
        sets all necessary updates and flushes them

        """

        if self.algorithm.array().lowest_point:
            self.current_points = self.algorithm.array().lowest_point
            self._update_lowest_point(self.current_points)
        else:
            self._update_lowest_point([])
        
        if self.algorithm.array().nextpoint:
            self.current_points = self.algorithm.array().nextpoint
            self._update_nextpoint(self.current_points)
        else:
            self._update_nextpoint([(), 'black'])

        # change plot with new x, y values (points)
        if self.algorithm.array().points:
            self.current_points = self.algorithm.array().points
            self._update_figure_points(self.current_points)
        else:
            self._update_figure_points([])

        # change plot with new vectors
        if self.algorithm.array().vectors:
            vectors = self.algorithm.array().vectors
            self._update_figure_vectors(vectors)
        else:
            self._update_figure_vectors([])

        # change plot with new lines
        if self.algorithm.array().lines:
            lines = self.algorithm.array().lines
            self._update_figure_lines(lines)
        else:
            self._update_figure_lines([])

        if self.algorithm.array().scatterpoints_position:
            scatterpos= self.algorithm.array().scatterpoints_position
            self.update_figure_scatter_points(scatterpos)
        else:
            self.update_figure_scatter_points(0, clear=True)

    def update_one_step(self, direction, play=False):
        """
        updates plot canvas and all other plot objects for one step in
        given diretion. Used for next/previous and play button.
        :param direction: direction of update related to buffer array (next or previous)
        :param play: determines if called from animation or one/last/first step call
        :return: current pseudocode position
        """

        if play:
            # sleep to make animation slower or faster
            self._sleep()

        if self.tracing_switch and self.current_points is not None:
            # traces current main point
            self._trace_current_focus()
            self.update_figure_plot()

        if self._check_boundaries(direction):
            if direction == "next":   # forwards
                self.algorithm.array.current_step += 1
            else:  # backwards
                self.algorithm.array.current_step -= 1

            # spinbox
            self.spinbox_currentposition.setValue(self.algorithm.array.current_step + 1)

            # update plot
            self.show_plot()

            # pseudocode update
            pseudocode_pos = self.algorithm.array().pseudocodeline

            return pseudocode_pos
        else:
            return None

    def update_figure_plot(self, reset=False, ObjectiveFunction=None):
        """
        updates figure curve with newly set limits.
        Called for example by navigation.
        :param reset: determines if function call has been made from reset button
        :param ObjectiveFunction: = none means, that no funcion has been chosen yet
        """
        if not(ObjectiveFunction or self.algorithm) or reset:
            x, y = (0, 0)
        else:
            # get x values for newly set limits
            x = np.linspace(self.axes.get_xlim()[0], self.axes.get_xlim()[1], 1000)
            # get y values from current algorithm
            if ObjectiveFunction:
                y = ObjectiveFunction(x)
            else:
                y = self.algorithm.ObjectiveFunction(x)

        # draw calculated x/y values
        self.curve.set_data(x, y)
        self.curve.figure.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def _update_figure_points(self, points):
        """
        updates points in plot
        :param points: contains x, y coordinates of to be added points
        """
        x_array, y_array = [], []
        for x, y in points:
            x_array.append(x)
            y_array.append(y)
        self.points.set_data(x_array, y_array)
        self.points.figure.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def update_figure_scatter_points(self, position, clear=False):
        """
        updates scatter points in plot
        :param position: current position in buffer array
        :param clear: boolean to remove scatter points
        """
        if clear or position == 0:
            if self.scatter_points:
                self.scatter_points.remove()
            self._init_scatter_points()
        else:
            points = np.array(self.algorithm.array.scatterpoint_array)[:position, :2]
            c = np.array(self.algorithm.array.scatterpoint_array)[:position, 2]
            self.scatter_points.set_offsets(points)
            self.scatter_points.set_array(c)
            self.colorbar.update_bruteforce(self.scatter_points)
            self.fig.get_axes()[1].set_visible(True)

        self.points.figure.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def _update_figure_vectors(self, vectors):
        """
        updates vectors in plot
        :param vectors: arrow coords from (x, y) to (x+dx, y+dy).
        """
        # delete old vectors
        for old_vector in self.vectors:
            old_vector.remove()
        # create new vectors
        self.vectors = []

        for x, y, dx, dy in vectors:
            arrow_length = np.sqrt(dx ** 2 + dy ** 2)
            axes_length = self.axes.get_ylim()[1] - self.axes.get_ylim()[0]
            if arrow_length > axes_length * 0.1:
                arrow_width = 0.008 * axes_length
                arrow_head_length = 0.2
            else:
                arrow_width = 0.2 * arrow_length
                arrow_head_length = arrow_length * 0.3
            arrow_head_width = arrow_width * 3
            self.vectors.append(self.axes.arrow(x, y, dx, dy,
                                                length_includes_head=True,
                                                width=arrow_width,
                                                head_length=arrow_head_length,
                                                head_width=arrow_head_width,
                                                fc='lightblue', ec='black'))
        self.curve.figure.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def _update_figure_lines(self, lines):
        """
        updates lines
        :param lines: line objects with start and end x, y coordinates
        """
        # delete old lines
        for line in self.lines:
            line[0].remove()
        # create new lines
        self.lines = []
        for x, y, end_x, end_y in lines:
            self.lines.append(self.axes.plot([x, end_x], [y, end_y], 'g--'))
        self.points.figure.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def _update_nextpoint(self, nextpoint):
        """
        updates nextpoint in plot
        :param nextpoint: x, y coordinates of next point
        """
        points, color = nextpoint
        x_array, y_array = [], []
        for x, y in points:
            x_array.append(x)
            y_array.append(y)
        self.nextpoint.set_color(color)
        self.nextpoint.set_data(x_array, y_array)
        self.nextpoint.figure.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def _update_lowest_point(self, lowest_points):
        """
        updates lowest_point in plot
        :param lowest_points: x, y coordinates of lowest point
        """
        x_array, y_array = [], []
        for x, y in lowest_points:
            x_array.append(x)
            y_array.append(y)
        self.lowest_point.set_data(x_array, y_array)
        self.lowest_point.figure.canvas.draw_idle()
        self.fig.canvas.flush_events()

#########
# Reset #
#########
    
    def reset_plot_objects(self):
        """
        reset plot objects (doesnt renew plotcanvas)
        """
        self._update_figure_points([])
        if self.algorithm is not None and self.algorithm.scatter is not None:
            self.update_figure_scatter_points(0, clear=True)
        self._update_figure_vectors([])
        self._update_figure_lines([])
        self.axes.set_ylim(0, 10)
        self.axes.set_xlim(-5, 5)

    def reset_figure(self):
        """
        resets curve
        """
        self.update_figure_plot(reset=True)

    def reset_plot(self):
        """
        called when reset button is clicked
        """
        # (re)set axes and grid
        self.axes.clear()
        self.axes.cla()
        self.axes.set_xlim(-5, 5)
        self.axes.set_ylim(0, 10)
        self.axes.grid(color='gray', alpha=0.5, linestyle='dashed', linewidth=0.5)

        # set origin axes
        self.axes.spines['left'].set_position('zero')  # x
        self.axes.spines['right'].set_color('none')
        self.axes.yaxis.tick_left()
        self.axes.spines['bottom'].set_position('zero')  # y
        self.axes.spines['top'].set_color('none')

        # init plot
        self._plot_inits()

################
# click points #
################

    def get_start_point(self, func):
        """
        connects click events to function that collects start point.
        :param func: function needs to be passed on to compute y point later
        :return: connect_id to unconnect after clicking start point points is finished
        """
        self.func = func
        # needs to be disconneted first as interpolated function that collects multiple and not just one
        # set of coordinates could be connected to the same event first
        self.fig.canvas.mpl_disconnect('button_press_event')
        connect_id = self.fig.canvas.mpl_connect('button_press_event', self._on_one_click)
        return connect_id

    def _on_one_click(self, click):
        """
        called from get_start_points. saves the last x value as start point and make the former
        clicked ones invisible.
        :param click: click event object that contains x, y coordinates
        """
        if click.xdata is not None and click.ydata is not None:
            x = click.xdata
            # calc y from func(x)
            y = self.func(x)
            # enqueue newest clicked point
            self.clicked_start_points.append(
                self.axes.plot(x, y, color="blue", marker='o', linestyle="dashed", markersize=4))
            # save start point
            self.start_point_click = x
            # make all but the last one invisible
            n = len(self.clicked_start_points)
            for p in self.clicked_start_points[:(n-1)]:
                p[0].set_visible(False)

    def get_clicked_coords(self):
        """
        connects click events to function that collects interpolated points
        :return: connect_id to unconnect after clicking points is finished
        """
        self.clicked_points = []
        # needs to be disconnected first (see get_start_point)
        self.fig.canvas.mpl_disconnect('button_press_event')
        connect_id = self.fig.canvas.mpl_connect('button_press_event', self._onclick)
        return connect_id

    def _onclick(self, click):
        """
        called by get_clicked_coords to get set of points on canvas
        """
        if click.xdata is not None and click.ydata is not None:
            self.clicked_points.append((click.xdata, click.ydata))
            new_point = self.clicked_points[len(self.clicked_points) - 1]
            self.points_for_interpolation.append(
                self.axes.plot(new_point[0], new_point[1], color='green', marker='o',
                               linestyle='dashed', markersize=2))

    def remove_interpolated_points(self):
        """
        set (the green) points that were used to display interpolated points as invisible
        """
        for p in self.points_for_interpolation:
            p[0].set_visible(False)

########################
# Helper defs and misc #
########################

    def set_axes(self, startpoint):
        """
        sets inital depending on funtion object and start point
        :param: startpoint: start point of calculation
        """
        y_min, y_max, x_min, x_max = self.algorithm.ObjectiveFunction.get_axes_parameters()

        if str(self.algorithm.ObjectiveFunction) == "Sinus" \
                or str(self.algorithm.ObjectiveFunction) == "Torsion Potential":
            tmp = x_min
            x_min = startpoint - (x_max - x_min) / 2
            x_max = startpoint + (x_max - tmp) / 2
        if str(self.algorithm.ObjectiveFunction) == "Interpolated" \
                or str(self.algorithm.ObjectiveFunction) == "Polynomial":
            if x_max < startpoint:
                x_max = startpoint + 1
            elif x_min > startpoint:
                x_min = startpoint - 1
            if y_max < self.algorithm.ObjectiveFunction(startpoint):
                y_max = self.algorithm.ObjectiveFunction(startpoint) + 1
            elif y_min > self.algorithm.ObjectiveFunction(startpoint):
                y_min = self.algorithm.ObjectiveFunction(startpoint) - 1

        self.axes.set_ylim(y_min, y_max)
        self.axes.set_xlim(x_min, x_max)

    def _sleep(self):
        """
        sleep between mouse x/y coords request
        (for better performance, rather then tracing mouse movements
        all the time)
        """
        loop = QEventLoop()
        QTimer.singleShot(self.sleep_time, loop.quit)
        loop.exec_()

    def _trace_current_focus(self):
        """
        tracing mode depening on zoom factor
        """
        x, y = self.current_points[0]
        self.axes.set_ylim(y-self.zoom, y+self.zoom)
        self.axes.set_xlim(x-self.zoom, x+self.zoom)

    def _check_boundaries(self, direction):
        """
        'if-overhead' for boundaries
        """
        if (direction == "next" and self.algorithm.array.current_step + 1 < len(self.algorithm.array)) or \
           (direction == "prev" and self.algorithm.array.current_step > 0):
            return True
        else:
            return False


