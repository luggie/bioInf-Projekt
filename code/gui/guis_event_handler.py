"""
Functions parser submodule for GUI.

This class works as intermediate interface between the static GUI and its functions.
It parses mouse clicks and pressed keys on the GUI (but not on the matplotlib canvas,
suchs as drag/move/zoom which are processes in visualization.navigation)

This is the only class that can directly alter GUI label texts, menu content, icons and
delete or add GUI content dynamically. The plot itself however is changed and updated in
visualization.plotcanvas but its instantiation is triggered here.
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
import sip
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QIcon, QPalette, QColor

# files from gui
from .gui import GuiMain
from .popup_guis_warnings import PopUpWarning, PopUpNotification
from .popup_guis_meths import PopUpMethods
from .popup_guis_obj_funcs import PopUpParameterPolynomial, PopUpFunction
from .popup_guis_settings import PopUpSettings
from .latex import mathtex_to_qpixmap, MathTexPixmapWidget
from .helpful_stuff import module_dir, _round

# modules from project
from visualization import CustomNavigationToolbar, PlotCanvas
from objective_functions import ObjectiveFunctions
from optimization import Algorithms

# </editor-fold>
########### IMPORTS ###########


class GuiFunctionParser(QMainWindow):
    """
    Functions parser class for GUI.
    See module docstring for explanation.

    """

    def __init__(self, main, plotcanvas):
        """
        Init
        :param main: see main.py
        :param plotcanvas: PlotCanvas object from submodule visualization
        """

        # main
        self.main = main

        # main ui implementation
        super(GuiFunctionParser, self).__init__()
        self.ui = GuiMain()
        self.ui.setupUi(self)

        # theme inits
        self._theme_inits()

        # function parameter
        self._init_inputs()

        # empty plot
        self._init_plot(plotcanvas)

        # buttons and other gui events
        self._connect_buttons()
        self._connect_spinbox()

        # set objective function and method menu
        self._fill_dropdown_menus()

        # populate main menu
        self._connect_main_menus()

        # Player mode
        self.player_mode = None

        # key events
        GuiFunctionParser.installEventFilter(self, self)

#########
# inits #
#########

    def _init_inputs(self):
        """
        Init variables for methods; functions and start point
        """
        # function
        self.function = None
        self.function_parameter = None
        self.function_object = None
        self.last_function = None
        self.last_function_chosen = None
        self.function_string = None
        self.function_string_plain = None
        self.choosing_points = False  # choosing points in interpolate function
        # methods
        self.method = None
        self.method_parameter = None
        self.method_object = None
        self.last_method = None
        self.last_method_chosen = None
        self.method_string = None
        self.method_heading = ""
        # start point
        self.startpoint = 2
        self.ui.label_start_point.setPixmap(mathtex_to_qpixmap("$x=2$", normal_theme=self.normal_theme))
        self.start_click_connect_id = None
        self.choosing_start_point = False
        # misc
        self.chosing_start_point_forbidden = False

    def _init_plot(self, plotcanvas):
        """
        Init empty plot
        :param plotcanvas: PlotCanvas object, initialized in main
        """
        self.PlotCanvas_object = plotcanvas
        self.PlotCanvas_object.spinbox_currentposition = self.ui.spinbox_currentposition
        self.ui.verticalLayout_plot_canvas.addWidget(self.PlotCanvas_object)
        self._init_toolbar()

    def _init_toolbar(self):
        """
        Init custom toolbar
        """
        self.toolbar = CustomNavigationToolbar(self.PlotCanvas_object, self)
        self.ui.verticalLayout_playerbottons.addWidget(self.toolbar, alignment=Qt.AlignLeft)

    def _connect_spinbox(self):
        """
        Connects spinbox to according function
        """
        self.ui.spinbox_currentposition.editingFinished.connect(self._spinbox_currentposition_changed)

    def _connect_buttons(self):
        """
        Connect Buttons with corresponding functions
        """
        # buttons
        self.ui.button_calculate.clicked.connect(self._button_calculate)
        self.ui.button_reset.clicked.connect(self._button_reset)
        self.ui.button_prev.clicked.connect(self._button_previous)
        self.ui.button_next.clicked.connect(self._button_next)
        self.ui.button_play_pause.clicked.connect(self._button_play_pause)
        self.ui.button_function_parameter.clicked.connect(self._button_function_parameters)
        self.ui.button_method_parameter.clicked.connect(self._button_method_parameters)
        self.ui.button_last.clicked.connect(self._button_last)
        self.ui.button_first.clicked.connect(self._button_first)

        # reset/set display, set button options when another function or method is selected
        self.ui.comboBox_function.currentTextChanged.connect(self._function_combobox_changed)
        self.ui.comboBox_method.currentTextChanged.connect(self._method_combobox_changed)

        # speed control
        self.ui.slider_speed.valueChanged.connect(self._speed_control)

        # start point
        self.ui.button_set_start_point.clicked.connect(self._set_start_point)

    def _connect_main_menus(self):
        """
        Connect main menu entries with functions
        """
        # file menu
        self.ui.menu_file_save.triggered.connect(self.toolbar.save_figure)
        self.ui.menu_file_exit.triggered.connect(self.close)
        # view menu
        self.ui.menu_view_trace.triggered.connect(self._tracing)
        self.ui.menu_view_theme.triggered.connect(self._toggle_stylesheet)
        # settings menu
        self.ui.menu_start_point.triggered.connect(self._startpoint)
        self.ui.menu_settings_plot.triggered.connect(self.toolbar.configure_subplots)
        self.ui.menu_settings_figure.triggered.connect(self.toolbar.edit_parameters)
        self.ui.menu_speed.triggered.connect(self._speed_window)
        # help menu
        self.ui.menu_settings_about.triggered.connect(self._about)
        self.ui.menu_settings_manual.triggered.connect(self._manual)

    def _fill_dropdown_menus(self):
        """
        Fill drop down menus 'methods' and 'functions'
        with available content
        """
        self.functions = list(ObjectiveFunctions.keys())
        for function in self.functions:
            self.ui.comboBox_function.addItem(function)

        # set method (algorithms)
        self.methods = list(Algorithms.keys())
        for method in self.methods:
            self.ui.comboBox_method.addItem(method)

    def _theme_inits(self):
        """
        Calls init functions for dark/normal theme
        """
        # app
        self._get_app()
        # main theme
        self._save_palette()
        # xy coords
        self._update_xy_coords_timer()
        # init theme mode
        self.normal_theme = True

##################
# dropdown menus #
##################

    def _function_combobox_changed(self):
        """
        Creates function object and distributes function parameter if already chosen
        to it among other function specific stuff
        Also calls plotting functions
        """
        if self.player_mode != "play":

            self.chosing_start_point_forbidden = False

            # reset plotcanvas to firmly erase colorbar if there
            self._rebuild_plotcanvas()

            # get function_object
            if self.ui.comboBox_function.currentText():
                self.function_object = ObjectiveFunctions[self.ui.comboBox_function.currentText()]

            # grey out for certain functions as they have no parameters
            if self.ui.comboBox_function.currentText() == "Sim. Ann. Nemesis":
                # disable method button
                self.ui.button_function_parameter.setEnabled(False)
                self.ui.button_function_parameter.setCheckable(False)
                self.ui.button_function_parameter.setText("Fixed parameters")

            elif self.ui.comboBox_function.currentText() == "Interpolated":
                self._button_function_parameters()  # to open choosing window at once
                # enable method button
                self.ui.button_function_parameter.setEnabled(True)
                self.ui.button_function_parameter.setCheckable(True)
                self.ui.button_function_parameter.setText("Set Parameters")

            # reset not yet set label
            elif self.last_function_chosen != self.ui.comboBox_function.currentText():
                # enable method button
                self.ui.button_function_parameter.setEnabled(True)
                self.ui.button_function_parameter.setCheckable(True)
                self.ui.button_function_parameter.setText("Set Parameters")

            # lsat function
            self.last_function_chosen = self.ui.comboBox_function.currentText()

            # set displayed formula
            # only sets defaults. when other coefficients are set, they overwrite these lines
            defaults = self.function_object.get_coeffs_defaults(self.function_object)
            function_string = self.function_object.create_formula_string(self.function_object, defaults)
            self.function_string_plain = function_string
            self.ui.label_function_parameters_show.setPixmap(mathtex_to_qpixmap(
                function_string, normal_theme=self.normal_theme))

            # set function default parameter:
            if self.ui.comboBox_function.currentText() != "Interpolated":
                self.function_parameter = defaults

        else:
            self.Warning = PopUpWarning("Please stop or pause animation first")
            self.Warning.exec_()

    def _method_combobox_changed(self):
        """
        Creates algorithm (method) object and distributes parameter if already chosen
        to it among other method specific stuff
        """
        if self.player_mode != "play":

            self.chosing_start_point_forbidden = False

            self.ui.label_method_parameters_show.setFont(self.ui.non_italic_font)

            # get object
            if self.ui.comboBox_method.currentText():
                self.method_object = Algorithms[self.ui.comboBox_method.currentText()]

            # last method
            self.last_method_chosen = self.ui.comboBox_method.currentText()

            # set displayed formula
            defaults = self.method_object.get_params(self.method_object)
            params_string = self.method_object.create_params_string(self.method_object, defaults)
            self.ui.label_method_parameters_show.setText(params_string)
            self.last_method_chosen = self.ui.comboBox_method.currentText()

            # set function default parameter:
            defaults = self.method_object.get_params_defaults(self.method_object)
            self.method_parameter = defaults

            # reset plotcanvas to firmly erase colorbar if there
            self._rebuild_plotcanvas()

            # plot again
            if self.function_object:
                function = self.function_object(self.function_parameter)
                self.PlotCanvas_object.update_figure_plot(ObjectiveFunction=function)
                # plot update
                self.function = self.ui.comboBox_function.currentText().replace(" ", "")
                self.PlotCanvas_object.set_algorithm(self.method_object)  
        else:
            self.Warning = PopUpWarning("Please stop or pause animation first")
            self.Warning.exec_()

##################
# Player Buttons #
##################

    def _button_previous(self):
        """
        Is activated when button 'previous' in player button menu is clicked.
        Returns to last step in buffer array and sets corresponding pseudo code
        line and figure step in plotcanvas.
        """
        if self._button_overhead() and self.player_mode == "pause":
            pseudocode_pos = self.PlotCanvas_object.update_one_step(direction="prev")
            if pseudocode_pos:
                self.ui.set_pseudocode(pseudocode_pos)

    def _button_next(self):
        """
        Is activated when button 'next' in player button menu is clicked.
        Proceeds to next step in buffer array and sets corresponding pseudo code
        line and figure step in plotcanvas.
        """
        if self._button_overhead() and self.player_mode == "pause":
            pseudocode_pos = self.PlotCanvas_object.update_one_step(direction="next")
            if pseudocode_pos:
                self.ui.set_pseudocode(pseudocode_pos)

    def _button_play_pause(self):
        """
        Is activated when button 'play' in player button menu is clicked.
        Iterates through play_animation in plotcanvas who's generator returns pseudo code
        line and player mode information to be passed on to pseudo code label and the buttons icon.
        Every first click will start (respectively resume) the animation, every second one will pause it
        """

        if self.player_mode == "pause" and self.PlotCanvas_object.algorithm is not None and \
                not self.PlotCanvas_object.algorithm.array.last_position():
            self._set_pause_button()
            # assert algorithm already chosen
            if self._button_overhead():
                self.player_mode = "play"
                pseudocodeline = self.PlotCanvas_object.algorithm.array().pseudocodeline
                while pseudocodeline != None and self.player_mode == "play" and \
                        not self.PlotCanvas_object.algorithm.array.last_position():
                    # update plot
                    pseudocodeline = self.PlotCanvas_object.update_one_step("next", play=True)
                    self.ui.set_pseudocode(pseudocodeline)
        elif self.PlotCanvas_object.algorithm is None:
            PopUpWarn = PopUpWarning("Please click calculate first")
            PopUpWarn.exec_()

        self.player_mode = "pause"
        self._set_play_button()

    def _button_last(self):
        """
        Is activated when button 'last' in player button menu is clicked.
        Shows last 'frame' in buffer array
        """
        if self._button_overhead() and self.player_mode == "pause":
            self.PlotCanvas_object.algorithm.array.current_step = \
                self.PlotCanvas_object.algorithm.array.next_empty_postiton - 1  # object chain lol
            self.ui.spinbox_currentposition.setValue(self.PlotCanvas_object.algorithm.array.next_empty_postiton)
            pseudocode_pos = self.PlotCanvas_object.algorithm.array().pseudocodeline
            self.ui.set_pseudocode(pseudocode_pos)
            self.PlotCanvas_object.show_plot()

    def _button_first(self):
        """
        Is activated when button 'first' in player button menu is clicked.
        Shows first 'frame' in buffer array
        """
        if self._button_overhead() and self.player_mode == "pause":
            self.PlotCanvas_object.algorithm.array.current_step = 0
            self.ui.spinbox_currentposition.setValue(1)
            pseudocode_pos = self.PlotCanvas_object.algorithm.array().pseudocodeline  # object chain lol
            self.ui.set_pseudocode(pseudocode_pos)
            self.PlotCanvas_object.show_plot()

###########################
# other buttons and menus #
###########################

    def _button_calculate(self):
        """
        Is activated when button 'calculate' is clicked.
        Gets current selected method and function type from GUI combo boxes and passes them on
        to plotcanvas object
        """

        # check if method and function and corresponding parameters are selected
        if self._everything_is_chosen() and self.startpoint:

            self.PlotCanvas_object.reset_plot()

            self.PlotCanvas_object.set_algorithm(self.main.calculate(self.function_object,
                                                                     self.function_parameter,
                                                                     self.method_object,
                                                                     self.method_parameter,
                                                                     self.startpoint))

            # pseudocode
            self.ui.label_animation_pseudocode.table_pseudocode.clear()

            # cast pseudocode lines onto qlistwidget (with some detours)
            self._fill_pseudocode_lines()

            table_pseudocode_height = len(self.PlotCanvas_object.algorithm.pseudocode) * 35
            self.ui.label_animation_pseudocode.table_pseudocode.setFixedSize(200, table_pseudocode_height)

            if self.PlotCanvas_object.algorithm.scatter:
                self.PlotCanvas_object.update_figure_scatter_points(None, clear=True)

            # update spinbox und arraylength
            self.ui.spinbox_currentposition.setValue(1)
            self.ui.spinbox_currentposition.setMinimum(1)
            self.ui.spinbox_currentposition.setMaximum(len(self.PlotCanvas_object.algorithm.array))
            self.ui.label_arraylength.setText('/ ' + str(len(self.PlotCanvas_object.algorithm.array)))

            # plot update
            self.function = self.ui.comboBox_function.currentText().replace(" ", "")
            self.PlotCanvas_object.set_axes(self.startpoint)
            self.PlotCanvas_object.update_figure_plot()
            self.PlotCanvas_object.show_plot()
            self.ui.verticalLayout_plot_canvas.update()

            self.chosing_start_point_forbidden = True

        # notify popup
        else:
            self.Warning = PopUpWarning("Please choose method, function and according parameters")
            self.Warning.exec_()

    def _button_reset(self):
        """
        Is activated when button 'reset' is clicked.
        Resets plotcanvas and pseudo code line to initial state
        """
        if self.player_mode != "play":
            # reset inputs
            self._init_inputs()

            # reset displays
            self.ui.comboBox_function.currentTextChanged.disconnect()
            self.ui.comboBox_method.currentTextChanged.disconnect()
            self.ui.comboBox_function.setCurrentIndex(0)
            self.ui.comboBox_method.setCurrentIndex(0)
            self.ui.label_function_parameters_show.setText("    not set yet")
            self.ui.label_method_parameters_show.setText("    not set yet")
            self.ui.comboBox_function.currentTextChanged.connect(self._function_combobox_changed)
            self.ui.comboBox_method.currentTextChanged.connect(self._method_combobox_changed)

            self._rebuild_plotcanvas()

            # reset pseudocode
            self.ui.set_pseudocode(0)
            self._clear_pseudocode_lines()

            # reset buffer array (and therefore current_step)
            self.PlotCanvas_object.algorithm = None

            self.player_mode = None

            self.chosing_start_point_forbidden = False
        else:
            self.Warning = PopUpWarning("Please stop or pause animation first")
            self.Warning.exec_()

    def _button_function_parameters(self):
        """
        open new function parameter setter dialog
        when it closes with "ok" it stores the set parameters
        Subdivided in special popups and such that can be
        deducted from generic abstract base class
        """
        self.function = self.ui.comboBox_function.currentText().replace(" ", "")

        if self.ui.label_function_parameters_show.text() == "    not set yet":
            self.function_string = "not set yet"

        if not self.function:
            self.Warning = PopUpWarning("Please choose function")
            self.Warning.exec_()

        elif self.function == "Interpolated":
            self._last_function_setter("Interpolated")

            self.PopUpInformation = PopUpWarning(
                "Please choose at least 3 points to interpolate\nthrough by clicking them."
                "\n Press 'return' to accept points")
            if self.PopUpInformation.exec_():
                self.point_click_connect_id = self.PlotCanvas_object.get_clicked_coords()
                self.choosing_points = True
                self.please_choose_annotation = self.PlotCanvas_object.axes.annotate(
                    "Please choose at least 3 points to interpolate through"
                    "\n Press 'return' to accept.",
                    xy=(1, 1), xycoords='axes fraction',
                    fontsize=10,
                    horizontalalignment='right',
                    verticalalignment='top')
                # The 'return' key is handled by eventFilter() respectively _interpolate_accept_clicked_points()
            else:
                self._last_function_setter(None)

        elif self.function == "Polynomial":
            self._last_function_setter("Polynomial")
            self.PopUpParameter = PopUpParameterPolynomial(
                self.function_parameter, self.function_object, self.normal_theme)
            if self.PopUpParameter.exec_():
                self.function_parameter = self.PopUpParameter.function_coeffs
                self.function_string = self.PopUpParameter.coeff_string
                self.ui.label_function_parameters_show.setPixmap(self.function_string)
                # plot
                function = self.function_object(self.function_parameter)
                self.PlotCanvas_object.update_figure_plot(ObjectiveFunction=function)

        else:  # all other generic popups for objective functions
            self._last_function_setter(self.function)
            self.PopUpParameter = PopUpFunction(self.function_parameter, self.function_object, self.normal_theme)
            if self.PopUpParameter.exec_():
                self.function_parameter = self.PopUpParameter.function_coeffs
                self.function_string = self.PopUpParameter.coeff_string
                self.function_string_plain = self.PopUpParameter.coeff_string_plain
                self.ui.label_function_parameters_show.setPixmap(self.function_string)
                # plot
                function = self.function_object(self.function_parameter)
                self.PlotCanvas_object.update_figure_plot(ObjectiveFunction=function)

    def _button_method_parameters(self):
        """
        open new function parameter setter dialog
        when it closes with "ok" it stores the set parameters
        """
        self.method = self.ui.comboBox_method.currentText().replace(" ", "")

        if self.ui.label_function_parameters_show.text() == "    not set yet":
            self.method_string = "not set yet"

        if not self.method:
            self.Warning = PopUpWarning("Please choose method")
            self.Warning.exec_()
        else:
            self._last_method_setter(self.method)
            self.PopUpParameter = PopUpMethods(self.method_parameter, self.method_object)
            if self.PopUpParameter.exec_():
                self.method_parameter = self.PopUpParameter.method_parameters
                self.method_string = self.PopUpParameter.method_parameters_string
                self.ui.label_method_parameters_show.setText(self.PopUpParameter.method_parameters_string)

    def _about(self):
        """
        opens an about this program window
        :return:
        """
        about_text = ["NOViZ (Numerical Optimization Visualiser)\n",
                      "made by:\n",
                      "\t-Malte Korn\n",
                      "\t-Lukas Müller",
                      "\t-Sarah Gritzka\n",
                      "\t-Jonas Wember\n",
                      "\t-Sandra Mattern\n",
                      "Supervision:\n",
                      "\t-Prof. Dr. Andrew Torda\n",
                      "\t-Timur Olzhabaev"]
        self.PopupAbout = PopUpNotification(about_text)
        self.PopupAbout.exec_()

    def _manual(self):
        """
        opens a pdf window
        """
        # TODO
        self.PopupAbout = PopUpNotification("Manual to be inserted")
        self.PopupAbout.exec_()

##############
# Dark Theme #
##############

    def _toggle_stylesheet(self):
        """
        swtich between dark and normal theme
        """
        palette = QPalette()
        if self.app is not None:
            if self.normal_theme:
                # set dark theme colors
                palette.setColor(QPalette.Window, QColor(53, 53, 53))
                palette.setColor(QPalette.WindowText, Qt.white)
                palette.setColor(QPalette.Base, QColor(25, 25, 25))
                palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ToolTipBase, Qt.white)
                palette.setColor(QPalette.ToolTipText, Qt.white)
                palette.setColor(QPalette.Text, Qt.white)
                palette.setColor(QPalette.Button, QColor(53, 53, 53))
                palette.setColor(QPalette.ButtonText, Qt.white)
                palette.setColor(QPalette.BrightText, Qt.red)
                palette.setColor(QPalette.Link, QColor(42, 130, 218))
                palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
                palette.setColor(QPalette.HighlightedText, Qt.black)
                self.app.setPalette(palette)
                # set attributes
                self.normal_theme = False
                self.ui.menu_view_theme.setText("Normal Theme")
                # set matplotlib properties
                self.PlotCanvas_object.axes.set_facecolor((0.25, 0.25, 0.25))
                self.PlotCanvas_object.fig.set_facecolor((0.25, 0.25, 0.25))
                self.PlotCanvas_object.points.figure.canvas.draw_idle()
                self.PlotCanvas_object.fig.canvas.flush_events()
                # player buttons
                self.ui.first_icon = QIcon(module_dir + 'gui_imgs/first_dt.png')
                self.ui.button_first.setIcon(self.ui.first_icon)
                self.ui.prev_icon = QIcon(module_dir + 'gui_imgs/prev_dt.png')
                self.ui.button_prev.setIcon(self.ui.prev_icon)
                if self.player_mode == "play":
                    self.ui.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/pause_dt.png')
                else:
                    self.ui.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/play_dt.png')
                self.ui.button_play_pause.setIcon(self.ui.button_play_pause_icon)
                self.ui.next_icon = QIcon(module_dir + 'gui_imgs/next_dt.png')
                self.ui.button_next.setIcon(self.ui.next_icon)
                self.ui.last_icon = QIcon(module_dir + 'gui_imgs/last_dt.png')
                self.ui.button_last.setIcon(self.ui.last_icon)
                # main icon
                self.ui.MainWindow.setWindowIcon(QIcon(module_dir + 'gui_imgs/NoviZ5.png'))

            else:
                # set default theme colors saved in _save_palette()
                palette.setColor(QPalette.Window, self.window_color)
                palette.setColor(QPalette.WindowText,  self.window_text_color)
                palette.setColor(QPalette.Base, self.base_color)
                palette.setColor(QPalette.AlternateBase, self.alternate_base_color)
                palette.setColor(QPalette.ToolTipBase, self.tool_tip_base_color)
                palette.setColor(QPalette.ToolTipText, self.tool_tip_text_color)
                palette.setColor(QPalette.Text, self.text_color)
                palette.setColor(QPalette.Button, self.button_color)
                palette.setColor(QPalette.ButtonText, self.button_text_color)
                palette.setColor(QPalette.BrightText, self.bright_text_color)
                palette.setColor(QPalette.Link, self.link_color)
                palette.setColor(QPalette.Highlight, self.highlight_color)
                palette.setColor(QPalette.HighlightedText, self.highlighted_text_color)
                self.app.setPalette(palette)
                # set attributes
                self.normal_theme = True
                self.ui.menu_view_theme.setText("Dark Theme")
                # set matplotlib properties
                self.PlotCanvas_object.axes.set_facecolor((0.94, 0.94, 0.94))
                self.PlotCanvas_object.fig.set_facecolor((0.94, 0.94, 0.94))
                self.PlotCanvas_object.points.figure.canvas.draw_idle()
                self.PlotCanvas_object.fig.canvas.flush_events()
                # player buttons
                self.ui.first_icon = QIcon(module_dir + 'gui_imgs/first.png')
                self.ui.button_first.setIcon(self.ui.first_icon)
                self.ui.prev_icon = QIcon(module_dir + 'gui_imgs/prev.png')
                self.ui.button_prev.setIcon(self.ui.prev_icon)
                if self.player_mode == "play":
                    self.ui.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/pause.png')
                else:
                    self.ui.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/play.png')
                self.ui.button_play_pause.setIcon(self.ui.button_play_pause_icon)
                self.ui.next_icon = QIcon(module_dir + 'gui_imgs/next.png')
                self.ui.button_next.setIcon(self.ui.next_icon)
                self.ui.last_icon = QIcon(module_dir + 'gui_imgs/last.png')
                self.ui.button_last.setIcon(self.ui.last_icon)
                # main icon
                self.ui.MainWindow.setWindowIcon(QIcon(module_dir + 'gui_imgs/NoviZ4.png'))

            # redraw pseudocode lines
            if self.PlotCanvas_object.algorithm is not None:
                self._fill_pseudocode_lines()
            # function string color
            if self.function_string_plain is not None:
                self.ui.label_function_parameters_show.setPixmap(mathtex_to_qpixmap(
                    self.function_string_plain, normal_theme=self.normal_theme))
            # redraw start point
            if self.PlotCanvas_object.start_point_click:
                txt = "$x=" + str(round(self.PlotCanvas_object.start_point_click, 2)) + "$"
            else:
                txt = "$x=" + str(self.startpoint) + "$"
            self.ui.label_start_point.setPixmap(mathtex_to_qpixmap(txt, normal_theme=self.normal_theme))

    def _save_palette(self):
        """
        saves default color palette (normal mode) to retrieve it again, when once changed to dark theme
        """
        self.normal_theme = True
        default_palette = QPalette()
        # save all default entities as there seems to be no setStandard() method
        self.window_color = QPalette.window(default_palette).color()
        self.window_text_color = QPalette.windowText(default_palette).color()
        self.base_color = QPalette.base(default_palette).color()
        self.alternate_base_color = QPalette.alternateBase(default_palette).color()
        self.tool_tip_base_color = QPalette.toolTipBase(default_palette).color()
        self.tool_tip_text_color = QPalette.toolTipText(default_palette).color()
        self.text_color = QPalette.text(default_palette).color()
        self.button_color = QPalette.button(default_palette).color()
        self.button_text_color = QPalette.buttonText(default_palette).color()
        self.bright_text_color = QPalette.brightText(default_palette).color()
        self.link_color = QPalette.link(default_palette).color()
        self.highlight_color = QPalette.highlight(default_palette).color()
        self.highlighted_text_color = QPalette.highlightedText(default_palette).color()

    def _get_app(self):
        """
        get QApplication instance to set common style for all platforms
        """
        try:
            self.app = QApplication.instance()
            self.app.setStyle("Fusion")
        except FileNotFoundError:
            self.PopUpApp = PopUpWarning("QApplication could not be found")
            self.PopUpApp.exec_()

###########
# hotkeys #
###########

    def eventFilter(self, source, event):
        """
        overwrites eventfilter, installed on self
        somehow another function caches some keys like
        arrow.
        :param: source: used by eventFilter super class
        :param: event: event object that stores ex. pressed keys
        """
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_F12:
                # f12 -> exit
                self.close()

            elif event.key() == Qt.Key_Return:
                # enter = accept interpolated keys
                if self.function == "Interpolated" and self.choosing_points:
                    self._interpolate_accept_clicked_points()
                # respectively
                # enter = accept start point
                elif self.choosing_start_point:
                    self._start_point_accept()
                else:
                    pass

            elif event.key() == Qt.Key_Space:
                # space = pause
                self._button_play_pause()
        return super(GuiFunctionParser, self).eventFilter(source, event)

###############
# start point #
###############

    def _set_start_point(self):
        """
        Opens notification window to inform user about start point settings.
        Collects last clicked x value as start point
        """
        if not self.chosing_start_point_forbidden:
            self.choosing_start_point = True
            if self._everything_is_chosen():
                PopUpInfo = PopUpNotification("Please select a starting point\nPress Enter to accept it")
                self.choose_start_point_annotation = self.PlotCanvas_object.axes.annotate(
                    "Please choose a start point"
                    "\n Press 'return' to accept.",
                    xy=(1, 1), xycoords='axes fraction',
                    fontsize=10,
                    horizontalalignment='right',
                    verticalalignment='top')
                func = self.function_object(self.function_parameter)
                if PopUpInfo.exec_():
                    self.start_click_connect_id = self.PlotCanvas_object.get_start_point(func)
            else:
                PopUpInfo = PopUpWarning("Please choose function and method first")
                PopUpInfo.exec_()
        else:
            PopUpInfo = PopUpWarning("Please reset plot again")
            PopUpInfo.exec_()

    def _start_point_accept(self):
        """
        called by eventFilter when enter is pressed after start point clicking
        """
        # end the points selection
        self.PlotCanvas_object.fig.canvas.mpl_disconnect(self.start_click_connect_id)
        # startpoint
        if self.PlotCanvas_object.start_point_click:
            # if point as been clicked
            self.startpoint = self.PlotCanvas_object.start_point_click
            for p in self.PlotCanvas_object.clicked_start_points:
                p[0].set_visible(False)
            # else: start point left at default or set via top menu

            txt = "$x=" + str(round(self.PlotCanvas_object.start_point_click, 2)) + "$"
        else:
            txt = "$x=" + str(self.startpoint) + "$"
        self.ui.label_start_point.setPixmap(mathtex_to_qpixmap(txt, normal_theme=self.normal_theme))
        self.choose_start_point_annotation.remove()
        self.choosing_start_point = False
        self.PlotCanvas_object.curve.figure.canvas.draw_idle()
        self.PlotCanvas_object.fig.canvas.flush_events()

    def _startpoint(self):
        """
        opens start point window from main menu
        """
        # Start point setter pop up from top menu
        self.PopUpParameter = PopUpSettings({"Start point": self.startpoint}, "Start point", 2)
        if self.PopUpParameter.exec_():
            settings_dict = self.PopUpParameter.params_dict
            self.startpoint = settings_dict["Start point"]
            txt = "$x=" + str(_round(self.startpoint)) + "$"
            self.ui.label_start_point.setPixmap(mathtex_to_qpixmap(txt, normal_theme=self.normal_theme))

######################
# help defs and misc #
######################

    def _spinbox_currentposition_changed(self):
        """
        Activated when a new value is entered in frame spinbox
        sets plotcanvas object and pseudo code line accordingly
        """
        if self._button_overhead() and self.player_mode == "pause":
            self.PlotCanvas_object.algorithm.array.current_step = self.ui.spinbox_currentposition.value() - 1
            pseudocode_pos = self.PlotCanvas_object.algorithm.array().pseudocodeline  # object chain lol
            self.ui.set_pseudocode(pseudocode_pos)
            self.PlotCanvas_object.show_plot()

    def _button_overhead(self):
        """
        Often used button exception
        """
        if self.PlotCanvas_object.algorithm is None:
            self.Warning = PopUpWarning("Please press calculate first")
            self.Warning.exec_()
            return False
        else:
            return True

    def _last_function_setter(self, function_name):
        """
        Checks if the parameter of the current chosen function have been
        chosen before and keeps ore deletes function parameters accordingly
        :param function_name: name of chosen function
        """
        if self.last_function is not None and self.last_function != function_name:
            self.function_parameter = None
        self.last_function = function_name

    def _last_method_setter(self, method_name):
        """
        Checks if the parameter of the current chosen method have been
        chosen before and keeps ore deletes method parameters accordingly
        :param method_name: name of chosen method
        """
        if self.last_method is not None and self.last_method != method_name:
            self.method_parameter = None
        self.last_method = method_name

    def _interpolate_accept_clicked_points(self):
        """
        function that handles chosen points for interpolate objective function.
        activated when 'return' key is pressed
        """
        # in interpolated function return key is used to
        # end the points selection
        self.PlotCanvas_object.fig.canvas.mpl_disconnect(self.point_click_connect_id)
        if self.start_click_connect_id:
            # if start point has been chosen before. the same signal slot is used so this needs to be disconencted first
            self.PlotCanvas_object.fig.canvas.mpl_disconnect(self.start_click_connect_id)
        # function parameter to be send to calculate in main
        self.function_parameter = self.PlotCanvas_object.clicked_points
        if len(self.function_parameter) < 3:
            self.PopUpInformation = PopUpNotification("Please choose at least 3 points to interpolate.")
            self.PopUpInformation.exec_()
        # set method string to display on gui
        self.method_string = "Points:\n"
        count = 0
        for point in self.function_parameter:
            self.method_string += "$x_" + str(count) + "$: " + str(round(point[0], 2)) + \
                                  ", " + \
                                  "$y_" + str(count) + "$: " + str(round(point[1], 2)) + "\n"
            count += 1
        self.method_string = mathtex_to_qpixmap(self.method_string, normal_theme=self.normal_theme )
        self.ui.label_function_parameters_show.setPixmap(self.method_string)
        # remove intermediate stuff
        self.please_choose_annotation.remove()
        self.PlotCanvas_object.remove_interpolated_points()

        self.choosing_points = False  # to end eventFilter from listening to "return key" signal

        # plot function
        function = self.function_object(self.function_parameter)
        self.PlotCanvas_object.update_figure_plot(ObjectiveFunction=function)

        # disconnect button event
        self.PlotCanvas_object.fig.canvas.mpl_disconnect('button_press_event')

    def _speed_control(self):
        """
        Converts speed slider value to wait factor which determines the animation speed
        """
        wait_factor = (100 - self.ui.slider_speed.value()) * 10
        self.PlotCanvas_object.sleep_time = wait_factor

    def _speed_window(self):
        """
        Opens speed setting window
        """
        # animation speed setter pop up
        speed = -(self.PlotCanvas_object.sleep_time / 10 - 100)
        self.PopUpSpeed = PopUpSettings({"Animation speed": speed}, "Animation speed", 500)
        if self.PopUpSpeed.exec_():
            settings_dict = self.PopUpSpeed.params_dict
            speed = settings_dict["Animation speed"]
            self.PlotCanvas_object.sleep_time = (100 - speed) * 10
            # set slider
            self.ui.slider_speed.setValue(speed)

    def _fill_pseudocode_lines(self):
        """
        Fill and format pseudocode table lines
        """
        table = self.ui.label_animation_pseudocode.table_pseudocode
        num_lines = len(self.PlotCanvas_object.algorithm.pseudocode)
        table.setRowCount(num_lines)

        i = 0
        for line in self.PlotCanvas_object.algorithm.pseudocode:
            tex_line = MathTexPixmapWidget(mathtex_to_qpixmap(line, fontsize=8, normal_theme=self.normal_theme))
            table.setCellWidget(i, 0, tex_line)
            i += 1
            table.setRowHeight(i, 25)

    def _clear_pseudocode_lines(self):
        """
        Clear pseudocode table
        """
        table = self.ui.label_animation_pseudocode.table_pseudocode
        table.setRowCount(0)

    def _tracing(self):
        """
        Opens tracing settings window and sets them accordingly
        """
        self.PopUpTracing = PopUpSettings(parameters={"Tracing": self.PlotCanvas_object.tracing_switch,
                                                      "Zoom": self.PlotCanvas_object.zoom},
                                          sender="Focus tracing",
                                          defaults=[False, 5])
        if self.PopUpTracing.exec_():
            settings_dict = self.PopUpTracing.params_dict
            self.PlotCanvas_object.tracing_switch = settings_dict["Tracing"]
            self.PlotCanvas_object.zoom = settings_dict["Zoom"]

    def _set_pause_button(self):
        """
        Sets pause button according to current theme
        """
        if self.normal_theme:
            self.ui.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/pause.png')
        else:
            self.ui.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/pause_dt.png')
        self.ui.button_play_pause.setIcon(self.ui.button_play_pause_icon)

    def _set_play_button(self):
        """
        Sets play button according to current theme
        """
        if self.normal_theme:
            self.ui.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/play.png')
        else:
            self.ui.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/play_dt.png')
        self.ui.button_play_pause.setIcon(self.ui.button_play_pause_icon)

    def _update_xy_coords(self):
        """
        Shows current xy position of mouse
        """
        x = self.PlotCanvas_object.current_x
        y = self.PlotCanvas_object.current_y
        xy = "x: {:3.2f} | y: {:3.2f}".format(x, y)
        self.ui.label_xy.setText(xy)

    def _update_xy_coords_timer(self):
        """
        Updates current xy position of mouse every 25 ms as constant tracing would cost to much performance
        """
        timer = QTimer(self)
        timer.timeout.connect(self._update_xy_coords)
        timer.start(25)

    def _everything_is_chosen(self):
        """
        Often used button query
        """
        if self.function_object and self.function_parameter and self.method_object and self.method_parameter:
            return True
        else:
            return False

    def _rebuild_plotcanvas(self):
        """
        Kills current plotcanvas object to give birth o another.
        The circle of life
        """
        # remove plotcanvas object from gui
        self.ui.verticalLayout_plot_canvas.removeWidget(self.PlotCanvas_object)
        # delete, remove, destroy, crush, end, kill, shatter, smash, wreck, annul, butcher, erase, extinguish,
        # trash, nuke, vaporize plotcanvas object ONCE AND FOR ALL
        # (although ... its not really needed to destroy the object, if was fun anyway to get rid of a million
        # bugs that were caused by this undying object which was still lingering about somewhere)
        sip.delete(self.PlotCanvas_object)

        # rebuild plotcanvas object and put it into place
        self.PlotCanvas_object = PlotCanvas()
        self.ui.verticalLayout_plot_canvas.addWidget(self.PlotCanvas_object)
        # set spinbox
        self.PlotCanvas_object.spinbox_currentposition = self.ui.spinbox_currentposition

        # fix theme
        if self.normal_theme:
            self.PlotCanvas_object.axes.set_facecolor((0.94, 0.94, 0.94))
            self.PlotCanvas_object.fig.set_facecolor((0.94, 0.94, 0.94))
        else:
            self.PlotCanvas_object.axes.set_facecolor((0.25, 0.25, 0.25))
            self.PlotCanvas_object.fig.set_facecolor((0.25, 0.25, 0.25))
        self.PlotCanvas_object.points.figure.canvas.draw_idle()
        self.PlotCanvas_object.fig.canvas.flush_events()

        # renew toolbar
        self.ui.verticalLayout_playerbottons.removeWidget(self.toolbar)
        self._init_toolbar()
        self.ui.menu_file_save.triggered.disconnect()
        self.ui.menu_file_save.triggered.connect(self.toolbar.save_figure)

        self.chosing_start_point_forbidden = False
