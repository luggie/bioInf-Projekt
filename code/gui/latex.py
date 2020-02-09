"""
Helper functions that are used in gui module
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
import matplotlib as mpl
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

# </editor-fold>
########### IMPORTS ###########


class MathTexPixmapWidget(QWidget):
    """
    Widget which is used to add QPixmaps to QTableWidget cells.
    Inherits from QWidget
    """
    def __init__(self, img, parent=None):
        QWidget.__init__(self, parent)

        self.lbPixmap = QLabel(self)
        self.lbPixmap.setPixmap(img)


def mathtex_to_qpixmap(mathTex, fontsize=10, normal_theme=True):
    """
    Function that converts Latex string to QPixmap
    source: https://stackoverflow.com/questions/32035251/displaying-latex-in-pyqt-pyside-qtablewidget

    example with label:
            text = mathtex_to_qpixmap('$A_{\pi}$')
            self.some_label.setPixmap(text)

    example with table cell:
        text = CustomWidget(mathtex_to_qpixmap("$x^2"$"))
        self.some_table.setCellWidget(0, 0, text)

    :param mathTex: Latex input
    :param fontsize: fontsize
    :param normal_theme: determines font color
    :return: QPixmap of input string
    """
    # set up a mpl figure instance
    fig = mpl.figure.Figure()
    fig.patch.set_facecolor('none')
    fig.set_canvas(FigureCanvasAgg(fig))
    renderer = fig.canvas.get_renderer()

    # plot the mathTex expression
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.patch.set_facecolor('none')
    # set text color
    if normal_theme:
        fontcolor = "black"
    else:
        fontcolor = "white"
    # ax.text(_, X) <-- x altered to adjust for bigger tex formulas #1
    t = ax.text(0, 0.3, mathTex, horizontalalignment='left', verticalalignment='baseline',
                fontsize=fontsize, color=fontcolor)

    # fit figure size to text artist
    fwidth, fheight = fig.get_size_inches()
    fig_bbox = fig.get_window_extent(renderer)
    text_bbox = t.get_window_extent(renderer)
    tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
    tight_fheight = text_bbox.height * fheight / fig_bbox.height

    # tight_fheight+x <-- x altered to adjust for bigger tex formulas #2
    fig.set_size_inches(tight_fwidth, tight_fheight+0.1)

    # convert mpl figure to QPixmap
    buf, size = fig.canvas.print_to_buffer()
    qimage = QImage.rgbSwapped(QImage(buf, size[0], size[1], QImage.Format_ARGB32))
    qpixmap = QPixmap(qimage)

    return qpixmap


def detect_latex_in_string(text):
    """
    checks if text contains latex code
    :param text: input string
    :return: input text string if not latex and QPixmap of latex code if latex, latex boolean
    """
    latex = False
    if "$" in text:
        text = mathtex_to_qpixmap(text)
        latex = True
    return text, latex
