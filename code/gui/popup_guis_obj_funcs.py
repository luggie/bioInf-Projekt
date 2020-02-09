"""
PopUp GUI submodule.

includes classes for input pop ups for chosen function
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
from abc import ABCMeta, abstractmethod
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QTableWidget, \
    QTableWidgetItem

# files from gui
from .latex import mathtex_to_qpixmap, MathTexPixmapWidget
from .popup_guis_warnings import PopUpWarning
from .helpful_stuff import module_dir, TableColumnNoEdit, _round

# </editor-fold>
########### IMPORTS ###########


class PopUpFunction(QDialog):
    """
    Abstract Base Class, inherting from QDialog,
    extended by function specific parameter input popups
    generic for most functions.
    Information about coefficients are taken from objective function direclty
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, function_coeffs, function_object, normal_theme):
        """
        init
        :param function_coeffs: function coefficients
        :param function_object: function object
        :param normal_theme: bool for dark/normal theme
        """
        super(PopUpFunction, self).__init__()

        # get function object
        self.function_object = function_object

        # Presets
        self._presets(function_coeffs, normal_theme)

        # Main layout
        self._create_main_layout()

        # function_coeffs table
        self._create_coeffs_table()

        # down side
        self._create_down_side()

        # OK / cancel buttons
        self._create_buttons()

        # specials
        self._create_specials()

    def _presets(self, function_coeffs, normal_theme):
        """
        presettings
        :param function_coeffs: coefficients
        :param normal_theme: bool for dark/normal theme
        """
        self.italic_font = QFont()
        self.italic_font.setItalic(True)
        self.normal_font = QFont()
        self.normal_font.setItalic(False)
        self.normal_theme = normal_theme

        # if function parameter is not set yet
        if function_coeffs is None:
            self.first_time = True
            self.function_coeffs = []  # gets filled in _create_coeffs_table
            coeff = self.function_object.get_coeffs(self.function_object)
            for i in range(len(coeff)):
                self.function_coeffs.append(coeff[i].default)
        else:
            self.first_time = False
            self.function_coeffs = function_coeffs

    def _create_main_layout(self):
        """
        Set common main layout parameters
        """
        self.setWindowTitle("Set Function Parameter")
        self.icon_parameter = QIcon(module_dir + "gui_imgs/settings.png")
        self.setWindowIcon(self.icon_parameter)
        self.verticalLayout_main = QVBoxLayout()
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.setLayout(self.verticalLayout_main)

    def _create_coeffs_table(self):
        """
        create table of function_coeffs with default values or set values
        from corresponding entries in objective function respectively
        set function_coeffs
        """
        # horizontal layout
        # purpose: to put additional things left or right to
        # the main coeff table as in Polynimial (+/- buttons)
        self.horizontalLayout_parameter = QHBoxLayout()
        self.horizontalLayout_parameter.setObjectName("horizontalLayout_parameter")
        self.verticalLayout_main.addLayout(self.horizontalLayout_parameter)

        self.table_coeffs = QTableWidget(len(self.function_coeffs), 2)
        self._table_header()
        self.table_coeffs.setObjectName("table_coeffs")
        self.table_coeffs.setItemDelegateForColumn(0, TableColumnNoEdit())  # set col 0 read only
        for i in range(len(self.function_coeffs)):
            # set coeff name
            coeff = self.function_object.get_coeffs(self.function_object, len(self.function_coeffs))
            tex_param_name = MathTexPixmapWidget(mathtex_to_qpixmap(coeff[i].latex, normal_theme=self.normal_theme))
            self.table_coeffs.setCellWidget(i, 0, tex_param_name)
            # check if opened before
            if self.first_time:  # if so, set default function_coeffs
                self.table_coeffs.setItem(i, 1, QTableWidgetItem(str(coeff[i].default)))
            else:  # or already set function_coeffs
                self.table_coeffs.setItem(i, 1, QTableWidgetItem(str(_round(self.function_coeffs[i]))))

        self.horizontalLayout_parameter.addWidget(self.table_coeffs)
        # what to do if value is changed
        self.table_coeffs.itemChanged.connect(self._table_coeffs_value_changed)

    def _table_header(self):
        """
        Sets table headers
        """
        self.table_coeffs.setHorizontalHeaderLabels(["Variable", "Value"])
        self.table_coeffs.setVerticalHeaderLabels(["" for _ in range(len(self.function_coeffs))])

    def _create_down_side(self):
        """
        create parameter labels
        """
        self.horizontalLayout_display = QHBoxLayout()
        self.horizontalLayout_display.setObjectName("horizontalLayout_display")
        self.verticalLayout_main.addLayout(self.horizontalLayout_display)
        #   function label heading
        self.label_coeffs_head = QLabel()
        self.label_coeffs_head.setObjectName("label_coeffs_head")
        self.label_coeffs_head.setText("Function:")
        self.horizontalLayout_display.addWidget(self.label_coeffs_head)
        #   function label
        self.label_coeffs = QLabel()
        self.label_coeffs.setObjectName("label_coeffs")
        self.label_coeffs.setFont(self.italic_font)
        self.horizontalLayout_display.addWidget(self.label_coeffs)
        # set function string
        self.coeff_string = mathtex_to_qpixmap(self.function_object.create_formula_string(
            self.function_object, self.function_coeffs), normal_theme=self.normal_theme)
        self.coeff_string_plain = self.function_object.create_formula_string(
            self.function_object, self.function_coeffs)
        self.label_coeffs.setPixmap(self.coeff_string)

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

    @abstractmethod
    def _create_specials(self):
        """
        Function specific stuff
        """
        pass

    def _table_coeffs_value_changed(self, item):
        """
        called when any value is changed in coeff table to
        get coeff list and coeff list display string
        :param item: object of what has been changed
        """
        # if signal comes from second column
        if item == "del" or item.column() == 1:  # "del" is used when a row has been deleted as in Polynomial
            self.function_coeffs = []
            for i in range(self.table_coeffs.rowCount()):
                try:
                    # assert float input
                    add = float(self.table_coeffs.item(i, 1).text())
                    self.function_coeffs.append(add)
                except ValueError:
                    # display warning otherwise and reset cell
                    self.Warning = PopUpWarning("Please enter decimal number")
                    self.Warning.exec_()
                    self.function_coeffs.append(0)
                    self.table_coeffs.item(i, 1).setText("0")

        self.coeff_string = mathtex_to_qpixmap(self.function_object.create_formula_string(
            self.function_object, self.function_coeffs), normal_theme=self.normal_theme)
        self.coeff_string_plain = self.function_object.create_formula_string(
            self.function_object, self.function_coeffs)

        # set function string
        if self.coeff_string:
            self.label_coeffs.setPixmap(self.coeff_string)
            self.label_coeffs.setFont(self.normal_font)
        else:
            self.label_coeffs.setText("not set yet")
            self.label_coeffs.setFont(self.italic_font)

        self._table_header()


class PopUpParameterPolynomial(PopUpFunction):
    """
    Parameter input PopUp for Polynomial
    sets a list of parameters in the form which is expected by objecvtive function when closed with ok
    Inherits from abstract base class
    """
    def __init__(self, function_parameter, function_object, normal_theme):
        """
        init
        :param function_parameter: function parameters
        :param function_object: function object
        :param normal_theme: bool for dark/normal theme
        """
        super(PopUpParameterPolynomial, self).__init__(function_parameter, function_object, normal_theme)
        self.normal_theme = normal_theme

    def _create_specials(self):
        """
        add / remove coefficient button
        """
        #   button layout
        self.verticalLayout_buttons = QVBoxLayout()
        self.verticalLayout_buttons.setObjectName("verticalLayout_buttons")
        self.horizontalLayout_parameter.addLayout(self.verticalLayout_buttons)
        #       plus button
        self.button_plus = QPushButton()
        self.button_plus.setObjectName("button_plus")
        self.button_plus.setText("+")
        self.button_plus.setFixedSize(25, 25)
        self.button_plus.clicked.connect(self._add_coeff_table_row)
        self.verticalLayout_buttons.addWidget(self.button_plus)
        #       minus button
        self.button_minus = QPushButton()
        self.button_minus.setObjectName("button_minus")
        self.button_minus.setText("-")
        self.button_minus.setFixedSize(25, 25)
        self.button_minus.clicked.connect(self._rm_coeff_table_row)
        self.verticalLayout_buttons.addWidget(self.button_minus)

    def _add_coeff_table_row(self):
        """
        adds empty row to coeff table
        """
        self.table_coeffs.insertRow(self.table_coeffs.rowCount())
        if len(self.function_coeffs) == 1:
            coeff_text = MathTexPixmapWidget(mathtex_to_qpixmap("$x$", normal_theme=self.normal_theme))
        else:
            coeff_text = MathTexPixmapWidget(mathtex_to_qpixmap("$x^" + str(len(self.function_coeffs)) + "$",
                                             normal_theme=self.normal_theme))
        self.table_coeffs.setCellWidget(len(self.function_coeffs), 0, coeff_text)
        self.table_coeffs.setItem(len(self.function_coeffs), 1, QTableWidgetItem("0"))

    def _rm_coeff_table_row(self):
        """
        removes last row from coeff table
        """
        if len(self.function_coeffs) > 1:
            self.table_coeffs.removeRow(self.table_coeffs.rowCount() - 1)
            self._table_coeffs_value_changed("del")
