"""
Navigation submodule.

handles zooms and drag'n'drop events, invoked in plotcanvas and returns
new axes limits with corresponding function.

It also contains an custom version of the default matplotlib toolbar.
"""


########### IMPORTS ###########
#<editor-fold desc="Open">

# packages
import types
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NaviToolB

#</editor-fold>
########### IMPORTS ###########


def zoom(canvas_object, event):
    """
    Zoom function handles mouse wheel scrolls and refreshes plot
    with new set axe limits.
    :param canvas_object: canvas object of plot before event
    :param event: event object (here: mousewheel action)
    source: https://stackoverflow.com/a/56221433/5468372
    """
    # get namespace of event params
    canvas_object.axes = event.inaxes
    canvas_object.axes._pan_start = types.SimpleNamespace(
        lim=canvas_object.axes.viewLim.frozen(),
        trans=canvas_object.axes.transData.frozen(),
        trans_inverse=canvas_object.axes.transData.inverted().frozen(),
        bbox=canvas_object.axes.bbox.frozen(),
        x=event.x,
        y=event.y)

    # zoom up and down
    if event.button == 'up':
        canvas_object.axes.drag_pan(3, event.key, event.x + 20, event.y + 20)
    else:  # event.button == 'down':
        canvas_object.axes.drag_pan(3, event.key, event.x - 20, event.y - 20)

    # update curve
    canvas_object.update_figure_plot()

    # display zoom
    fig = canvas_object.axes.get_figure()
    fig.canvas.draw_idle()


def drag(canvas_object, event):
    """
    Function that handles the 'drag' in drag'n'drop.
    :param canvas_object: canvas object of plot before event
    :param event: event object (here: click in canvas)
    source: https://stackoverflow.com/a/32630930/5468372
    """
    # check if axes limits are exceeded
    if event.inaxes != canvas_object.axes:
        return

    # set drag params in PlotCanvas Objekt
    canvas_object.cur_xlim = canvas_object.axes.get_xlim()
    canvas_object.cur_ylim = canvas_object.axes.get_ylim()
    canvas_object.press = canvas_object.x0, canvas_object.y0, event.xdata, event.ydata
    canvas_object.x0, canvas_object.y0, canvas_object.xpress, canvas_object.ypress = canvas_object.press


def drop(canvas_object):
    """
    Function that handles the 'drop' in drag'n'drop.
    :param canvas_object: canvas object of plot before event
    source: https://stackoverflow.com/a/32630930/5468372
    """
    # "unpress"
    canvas_object.press = None
    # refresh canvas
    canvas_object.axes.figure.canvas.draw()


def move(canvas_object, event):
    """
    Function hat handles move between drag and drop in drag'n'drop.
    :param canvas_object: canvas object of plot before event
    :param event: event object (here: move in canvas between drag and drop)
    source: https://stackoverflow.com/a/32630930/5468372
    """
    # periodacally request mouse position
    print_mouse_coords(canvas_object, event)

    # check if "pressed" and if axes limits are exceeded
    if canvas_object.press is None:
        return
    if event.inaxes != canvas_object.axes:
        return

    # calc delta x/y
    dx = event.xdata - canvas_object.xpress
    dy = event.ydata - canvas_object.ypress

    # set new viertual x/y-lims
    canvas_object.cur_xlim -= dx
    canvas_object.cur_ylim -= dy

    # apply new virtual x/y-lims
    canvas_object.axes.set_xlim(canvas_object.cur_xlim)
    canvas_object.axes.set_ylim(canvas_object.cur_ylim)

    # update curve
    canvas_object.update_figure_plot()

    # draw new virtual x/y-lims
    canvas_object.axes.figure.canvas.draw()
    canvas_object.axes.figure.canvas.flush_events()


def print_mouse_coords(canvas_object, event):
    """
    sets x, y coordinates of event on
    :param canvas_object: plot canvas object
    :param event: mouse click event object containing x, y coordinates
    """
    # get mouse x,y coords to display
    x, y = event.xdata, event.ydata
    if x and y:
        canvas_object.current_x = x
        canvas_object.current_y = y


class CustomNavigationToolbar(NaviToolB):
    """
    Reduced custom toolbar of the default matplotlib toolbar that only offers
    some of its features.
    NaviToolB: abbreviated navigation toolbar from matploblib pyqt5 backend
    """
    toolitems = [tool for tool in NaviToolB.toolitems if tool[0] in ('Subplots', 'Save')]
