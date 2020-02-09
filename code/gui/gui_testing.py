"""
Test for gui module
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
from time import sleep

# files from gui
from .gui import GuiMain

# </editor-fold>
########### IMPORTS ###########


def test_calculate(qtbot):
    """
    Main test function
    :param qtbot: qtbot object for gui testing
    """
    window = GuiMain()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitForWindowShown(window)
    sleep(3)

    qtbot.mouseClick(window.comboBox_method)


if __name__ == '__main__':
    test_calculate()