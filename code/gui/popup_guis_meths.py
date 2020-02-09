"""
PopUp GUI submodule.

includes classes for input pop ups for chosen method
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
# from abc import ABCMeta, abstractmethod  # maybe to be used later when more special method pop ups might be needed
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem

# files from gui
from .popup_guis_warnings import PopUpWarning
from .helpful_stuff import module_dir, TableColumnNoEdit

# </editor-fold>
########### IMPORTS ###########


class PopUpMethods(QDialog):
    """
    Abstract Base Class, inherting from QDialog,
    extended by method specific parameter input popups
    """

    # maybe to be used later when more special method pop ups might be needed
    #_metaclass__ = ABCMeta

    def __init__(self, method_parameters, method_object):
        """
        init
        :param method_parameters: method parameters
        :param method_object: method object
        """
        super(PopUpMethods, self).__init__()

        self.method_object = method_object

        # presets
        self._presets(method_parameters)

        # Main layout
        self._create_main_layout()

        # parameter input table
        self._create_input_table()

        # ok / cancel buttons
        self._create_buttons()

        # postsets
        self._postsets()

    def _presets(self, method_parameters):
        """
        set fonts etc
        :param method_parameters: method parameters
        """
        self.italic_font = QFont()
        self.italic_font.setItalic(True)
        self.normal_font = QFont()
        self.normal_font.setItalic(False)

        # if method parameters are not set yet
        if method_parameters is None:
            self.first_time = True
            self.method_parameters = []
            params = self.method_object.get_params(self.method_object)
            for i in range(len(params)):
                self.method_parameters.append(params[i].default)
        else:
            self.first_time = False
            self.method_parameters = method_parameters

    def _create_main_layout(self):
        """
        Set common main layout parameters
        """
        self.setWindowTitle("Set Method Parameter")
        self.icon_parameter = QIcon(module_dir + "gui_imgs/settings.png")
        self.setWindowIcon(self.icon_parameter)
        self.verticalLayout_main = QVBoxLayout()
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.setLayout(self.verticalLayout_main)

    def _create_input_table(self):
        """
        creates table for input parameters
        """
        self.table_params = QTableWidget(len(self.method_parameters), 2)
        self.table_params.setObjectName("table_coeffs")
        self.table_params.setItemDelegateForColumn(0, TableColumnNoEdit())  # set col 0 read only
        for i in range(len(self.method_parameters)):
            # set coeff name
            params = self.method_object.get_params(self.method_object)
            self.table_params.setItem(i, 0, QTableWidgetItem(params[i].name))
            # check if opened before
            if self.first_time:  # if so, set default function_coeffs
                self.table_params.setItem(i, 1, QTableWidgetItem(str(params[i].default)))
            else:  # or already set function_coeffs
                self.table_params.setItem(i, 1, QTableWidgetItem(str(self.method_parameters[i])))

        self.verticalLayout_main.addWidget(self.table_params)
        # what to do if value is changed
        self.table_params.itemChanged.connect(self._table_params_value_changed)

    def _create_buttons(self):
        """
        OK / cancel buttons
        """
        self.buttons_okcancel = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox_okcancel = QDialogButtonBox(self.buttons_okcancel)
        self.buttonBox_okcancel.setObjectName("buttonBox_Warning")
        self.buttonBox_okcancel.accepted.connect(self.accept)
        self.buttonBox_okcancel.rejected.connect(self.reject)
        self.verticalLayout_main.addWidget(self.buttonBox_okcancel)

    def _create_method_string(self):
        """
        string from method parameters
        """
        self.method_parameters_string = ""
        params = self.method_object.get_params(self.method_object)
        for i in range(len(self.method_parameters)):
            self.method_parameters_string += params[i].name + ": " + str(self.method_parameters[i]) + "\n"

    def _table_params_value_changed(self, item):
        """
        called when any value is changed in coeff table to
        get coeff list and coeff list display string
        """
        # if signal comes from second column
        if item == "del" or item.column() == 1:  # "del" is used when a row has been deleted
            self.method_parameters = []
            for i in range(self.table_params.rowCount()):
                try:
                    # assert float input
                    add = float(self.table_params.item(i, 1).text())
                    self.method_parameters.append(add)
                except ValueError:
                    # display warning otherwise and reset cell
                    self.Warning = PopUpWarning("Please enter decimal number")
                    self.Warning.exec_()
                    self.method_parameters.append(0)
                    self.table_params.item(i, 1).setText("0")

        self._create_method_string()

    def _postsets(self):
        """
        creates method strings
        """
        self._create_method_string()
