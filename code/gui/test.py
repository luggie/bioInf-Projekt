"""
Test module for smoother move points.
The intended function would to a moving rather than a jumping point.
Under construction.
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

# </editor-fold>
########### IMPORTS ###########


class Gui(QWidget):
    """
    main window object
    """
    def __init__(self):
        """
        init
        """
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        set window geometries
        """
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Gui')
        self.verticalLayout_plot_canvas = QVBoxLayout(self)
        self.show()


class PlotCanvas(FigureCanvas):
    """
    toy plotcanvas object
    """
    def __init__(self):
        """
        init
        """
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.points = self.axes.plot([], [])[0]
        self.points_array = [(0, 1), (1, 2)]

    def _animate(self, x_start, y_start, i):
        """
        move point smootly from a
        :param x_start: start x value of animation
        :param y_start: start y value of animation
        :param i: iteration steps that the animation in FuncAnimation takes
        """

        x_target, y_target = self.points_array[1]
        diff_x = x_target - x_start
        diff_y = y_target - y_start
        x_intermediate = diff_x / (i + 1)
        y_intermediate = diff_y / (i + 1)
        self.points.set_data(x_intermediate, y_intermediate)

    def update(self):
        """
        starts an animation
        FuncAnimation has quite strict rule about what it wants and in which order
        """
        x_start, y_start = self.points_array[0]
        self.anim = FuncAnimation(self.fig, self._animate, fargs=(x_start, y_start), frames=100, interval=20)

    def show(self):
        """
        go!
        """
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Gui()
    sys.exit(app.exec_())
    canvas = PlotCanvas()
    Gui.verticalLayout_plot_canvas.addWidget(canvas)
    canvas.update()
    canvas.show()