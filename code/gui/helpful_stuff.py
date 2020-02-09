"""
Helper functions for gui module
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
import os
from PyQt5.QtWidgets import QItemDelegate, QPushButton
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

# </editor-fold>
########### IMPORTS ###########


# icon path for pushbuttons with relative folder path
module_dir = os.path.dirname(os.path.realpath(__file__)) + os.path.sep


def _round(num):
    """
    rounds if no decimal number for output string
    :param num: input number
    :return: rounded if num == x.0
    """
    if num % 1 == 0:
        return round(num)
    else:
        return num


class TableColumnNoEdit(QItemDelegate):
    """
    Sets Delegate to make a certain table entity read only
    source: https://stackoverflow.com/questions/24024815/set-a-whole-column-in-qtablewidget-read-only-in-python
    """

    def createEditor(self, *args):
        """
        overwrites createEditor function in QItemDelegate
        :param args: args to be passed on (read pyqt5 documentation on that matter for more information)
        :return: None (evokes non editable items)
        """
        return None


class ButtonOnOff(QPushButton):
    """
    Fancy on/off button.
    Modulated QPushbutton
    source: https://stackoverflow.com/questions/56806987/switch-button-in-pyqt
    """
    def __init__(self, parent=None):
        """
        init
        :param parent: parent of QPushButton. None by default
        """
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        """
        paints the fancy on/off button
        :param event: needs to be set, eventough no event is captured. It is so, because paintEvent is overwriting
            an existing function in QPushButton
        """
        label = "ON" if self.isChecked() else "OFF"
        bg_color = Qt.black

        radius = 10
        width = 32
        center = self.rect().center()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QColor(255, 255, 255))

        pen = QPen(Qt.gray)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush(QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)
