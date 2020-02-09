"""
PopUp GUI submodule.

includes classes for input pop ups for chosen settings in menu bar

If the value of ONE (only one allowed) param dict value is of type bool,
an on/off switch is included instead of float input table cell
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem, QSizePolicy

# files from gui
from .popup_guis_warnings import PopUpWarning
from .helpful_stuff import module_dir, TableColumnNoEdit, ButtonOnOff, _round

# </editor-fold>
########### IMPORTS ###########


class PopUpSettings(QDialog):
    """
    Base class inhereting from QDialog
    that is used to create popup windows
    for variable sets of parameters
    """
    def __init__(self, parameters, sender, defaults):
        """
        init
        :param parameters: dictionary of parameters  (see module description for further information)
        :param sender: who created the settings dialog
        :param defaults: default values of parameters that need to be set
        """
        super(PopUpSettings, self).__init__()

        self.parameters = parameters
        self.params_dict = self.parameters

        # Main layout
        self._create_main_layout(sender)

        # parameters input
        self._create_inputs(defaults)

        # OK / cancel buttons
        self._create_buttons()

    def _create_main_layout(self, sender):
        """
        Set common main layout parameters
        """
        self.setWindowTitle("Set " + sender)
        self.icon_parameter = QIcon(module_dir + "gui_imgs/settings.png")
        self.setWindowIcon(self.icon_parameter)
        self.verticalLayout_main = QVBoxLayout()
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.setLayout(self.verticalLayout_main)

    def _create_inputs(self, defaults):
        """
        create inputs for all existing parameters in table
        for floats: table entry
        for booleans: fancy on/off button
        :param defaults: default values of input/output parameters
        """
        self.table_parameter = QTableWidget(len(self.parameters), 2)
        self._table_header()
        self.table_parameter.setObjectName("table_parameter")
        self.table_parameter.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.table_parameter.setItemDelegateForColumn(0, TableColumnNoEdit())  # set col 0 read only
        i = 0
        for param, value in self.parameters.items():
            # set param name
            self.table_parameter.setItem(i, 0, QTableWidgetItem(str(param)))
            if value is not None:
                if isinstance(value, bool):
                    # on/off button for bool
                    self.bool_value = value
                    button_on_off = ButtonOnOff()
                    button_on_off.setChecked(value)
                    button_on_off.clicked.connect(self._button_switch)
                    self.table_parameter.setCellWidget(i, 1, button_on_off)
                else:
                    # float input otherwise # has to be str for some reason
                    self.table_parameter.setItem(i, 1, QTableWidgetItem(str(_round(value))))
            else:
                self.table_parameter.setItem(i, 1, QTableWidgetItem(str(_round(defaults[i]))))
            i += 1

        self.verticalLayout_main.addWidget(self.table_parameter)
        # what to do if value is changed
        self.table_parameter.itemChanged.connect(self._table_parameter_value_changed)

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

    def _table_parameter_value_changed(self, item):
        """
        called when any value is changed in param table to
        get param dict
        :param item
        """
        # if signal comes from second column or button on/off is toggled
        if item == "button_switched" or item.column() == 1:
            self.params_dict = {}
            for i in range(self.table_parameter.rowCount()):
                # if text aka float input
                param = str(self.table_parameter.item(i, 0).text())
                # assert float input
                if self.table_parameter.item(i, 1) is None:
                    # should be the cell with bool button at this point
                    self.params_dict[param] = self.bool_value
                else:
                    try:
                        add = float(self.table_parameter.item(i, 1).text())
                        self.params_dict[param] = add
                    except ValueError:
                        # display warning otherwise and reset cell
                        self.Warning = PopUpWarning("Please enter decimal number")
                        self.Warning.exec_()
                        self.params_dict[param] = 0
                        self.table_parameter.item(i, 1).setText("0")

        self._table_header()

    def _table_header(self):
        """
        set table headers
        """
        self.table_parameter.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.table_parameter.setVerticalHeaderLabels(["" for _ in range(len(self.parameters))])

    def _button_switch(self):
        """
        calls value changed function to set output parameters
        """
        if self.bool_value:
            self.bool_value = False
        else:
            self.bool_value = True
        self._table_parameter_value_changed("button_switched")
