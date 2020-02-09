"""
Pseudocode Submodule

Includes Pseudocode as MathTex, animation function and highlighting label
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
from PyQt5.QtCore import QPropertyAnimation, Qt, QPoint
from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget
from PyQt5.QtGui import QPainter, QPixmap

# </editor-fold>
########### IMPORTS ###########


class PseudocodeHighlightAnimation(QWidget):
    """
    Pseudocode text setter and highlight animation
    """
    def __init__(self):
        """
        init
        """
        super(PseudocodeHighlightAnimation, self).__init__()

        # empty init
        self.table_pseudocode = QTableWidget(self)
        self.table_pseudocode.setColumnCount(1)
        self.table_pseudocode.horizontalHeader().hide()
        self.table_pseudocode.verticalHeader().hide()
        self.table_pseudocode.setFixedWidth(200)
        self.table_pseudocode.setColumnWidth(0, 200)
        self.table_pseudocode.setShowGrid(False)

        # transparent label
        self.label_highlight = QLabel('', self)
        self.label_highlight_pixmap = QPixmap(200, 25)
        self.label_highlight_pixmap.fill(Qt.yellow)
        self.label_highlight.setPixmap(self.label_highlight_pixmap)
        self.label_highlight_trasparent_pixmap = QPixmap(self.label_highlight_pixmap.size())
        self.label_highlight_trasparent_pixmap.fill(Qt.transparent)
        #   make it transparent (magic)
        painter = QPainter(self.label_highlight_trasparent_pixmap)
        painter.setOpacity(0.5)
        painter.drawPixmap(QPoint(), self.label_highlight_pixmap)
        painter.end()
        self.label_highlight.setPixmap(self.label_highlight_trasparent_pixmap)

        # actual animation
        self.y = 0
        self.label_highlight_animation = QPropertyAnimation(self.label_highlight, b'pos')
        self.label_highlight_animation.setDuration(100)

    def move(self, pseudocode_pos):
        """
        move highlight label to:
        :param pseudocode_pos: new pseudo code line position
        """
        self.label_highlight_animation.setStartValue(QPoint(0, self.y))
        self.y = pseudocode_pos * 25
        self.label_highlight_animation.setEndValue(QPoint(0, self.y))
        self.label_highlight_animation.start()
