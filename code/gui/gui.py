"""
Static GUI submodule.

Creates GUI layouts, frames and content.
No dynamic changes are made.
The class is instantiated in functions_parser
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
from PyQt5.QtCore import QSize, Qt, QMetaObject
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout, QLabel, QComboBox, QWidget, \
    QStatusBar, QMenuBar, QAction, QSpinBox, QScrollArea, QSlider

# files from gui
from .pseudocode_animation import PseudocodeHighlightAnimation
from .helpful_stuff import module_dir

# </editor-fold>
########### IMPORTS ###########


class GuiMain(object):
    """
    Static GUI class
    See module docstring for explanation.
    """
    def setupUi(self, MainWindow):
        """
        __init__
        :param MainWindow: mainwindow object called in guis_event_handler.py
        """
        # Presets
        self._presets(MainWindow)

        # Main Frames
        # ***********************************************************
        self._main_frame()
        # ***********************************************************

        # Left Side
        # ***********************************************************
        self._left_side()
        # ***********************************************************

        # ***********************************************************
        # Right Side
        self._right_side()
        # ***********************************************************

        # Postsets
        self._postsets()

    def _main_frame(self):
        """
        Main layout and frame.
        Separation in left and right side.
        """
        self.MainWindow.resize(1200, 900)
        self.MainWindow.setWindowTitle("NOViZ")
        self.centralwidget = QWidget(self.MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.MainWindow.setWindowIcon(QIcon(module_dir + 'gui_imgs/NoviZ4.png'))

        # menu layout
        self.verticalLayout_menu = QVBoxLayout(self.centralwidget)
        self.verticalLayout_menu.setObjectName("verticalLayout_menu")
        self._add_menus_on_top()

        # main layout
        self.horizontalLayout_main = QHBoxLayout()
        self.horizontalLayout_main.setObjectName("verticalLayout_menu")
        self.verticalLayout_menu.addLayout(self.horizontalLayout_main)

        # left frame and left layout
        self.frame_left = QFrame()
        self.frame_left.setObjectName("frame_left")
        self.frame_left.setFrameShape(QFrame.StyledPanel)
        self.frame_left.setFrameShadow(QFrame.Plain)
        self.frame_left.setLineWidth(10)
        self.verticalLayout_left = QVBoxLayout(self.frame_left)
        self.verticalLayout_left.setObjectName("verticalLayout_left")
        self.horizontalLayout_main.addWidget(self.frame_left)

        # right frame and right layout
        self.frame_right = QFrame()
        self.frame_right.setObjectName("frame_right")
        self.frame_right.setFrameShape(QFrame.StyledPanel)
        self.frame_right.setFrameShadow(QFrame.Plain)
        self.frame_right.setLineWidth(10)
        self.verticalLayout_right = QVBoxLayout(self.frame_right)
        self.verticalLayout_right.setObjectName("verticalLayout_right")
        self.verticalLayout_right.setSizeConstraint(4)
        self.horizontalLayout_main.addWidget(self.frame_right)

    def _add_menus_on_top(self):
        """
        init main menu
        """
        # set up menu bar
        self.main_menu = QMenuBar()
        self.main_menu.setObjectName("main_menu")
        self.verticalLayout_menu.addWidget(self.main_menu)
        # menu entrys
        #   file menu
        self.file_menu = self.main_menu.addMenu('File')
        self.file_menu.setObjectName("file_menu")
        #       save
        self.menu_file_save = QAction("Save")
        self.menu_file_save.setShortcut('Ctrl+S')
        self.menu_file_save.setStatusTip('Save current image')
        self.menu_file_save.setObjectName("menu_file_save")
        self.file_menu.addAction(self.menu_file_save)
        #       exit
        self.menu_file_exit = QAction("Exit")
        self.menu_file_exit.setShortcut('Ctrl+Q')
        self.menu_file_exit.setStatusTip('Exit application')
        self.menu_file_exit.setObjectName("menu_file_exit")
        self.file_menu.addAction(self.menu_file_exit)

        #   view menu
        self.view_menu = self.main_menu.addMenu('View')
        self.view_menu.setObjectName("view_menu")
        #   tracing
        self.menu_view_trace = QAction("Focus tracing")
        self.menu_view_trace.setShortcut('Ctrl+Alt+T')
        self.menu_view_trace.setStatusTip("Trace current point")
        self.menu_view_trace.setObjectName("menu_view_trace")
        self.view_menu.addAction(self.menu_view_trace)
        #    dark theme
        self.menu_view_theme = QAction("Dark theme")
        self.menu_view_theme.setShortcut('Ctrl+Alt+D')
        self.menu_view_theme.setStatusTip("Activate dark theme")
        self.menu_view_theme.setObjectName("menu_view_theme")
        self.view_menu.addAction(self.menu_view_theme)

        #   settings menu
        self.settings_menu = self.main_menu.addMenu('Settings')
        self.settings_menu.setObjectName("settings_menu")
        #       figure setup
        self.menu_settings_figure = QAction("Figure setup")
        self.menu_settings_figure.setShortcut('Ctrl+Alt+F')
        self.menu_settings_figure.setStatusTip('Figure setup')
        self.menu_settings_figure.setObjectName("menu_settings_figure")
        self.settings_menu.addAction(self.menu_settings_figure)
        #       plot setup
        self.menu_settings_plot = QAction("Plot setup")
        self.menu_settings_plot.setShortcut('Ctrl+Alt+P')
        self.menu_settings_plot.setStatusTip('Plot setup')
        self.menu_settings_plot.setObjectName("menu_settings_plot")
        self.settings_menu.addAction(self.menu_settings_plot)
        self.settings_menu.addSeparator()
        #       start point
        self.menu_start_point = QAction("Start point")
        self.menu_start_point.setShortcut('Ctrl+Alt+S')
        self.menu_start_point.setStatusTip('Set start point')
        self.menu_start_point.setObjectName("menu_start_point")
        self.settings_menu.addAction(self.menu_start_point)
        #       speed
        self.menu_speed = QAction("Animation Speed")
        self.menu_speed.setShortcut('Ctrl+Alt+.')
        self.menu_speed.setStatusTip('Set animatio speed')
        self.menu_speed.setObjectName('menu_speed')
        self.settings_menu.addAction(self.menu_speed)

        #   help menu
        self.help_menu = self.main_menu.addMenu('Help')
        self.help_menu.setObjectName("help_menu")
        #       Manual
        self.menu_settings_manual = QAction("Manual")
        self.menu_settings_manual.setShortcut('Ctrl+Alt+M')
        self.menu_settings_manual.setStatusTip('Open Manual')
        self.menu_settings_manual.setObjectName("menu_settings_manual")
        self.help_menu.addAction(self.menu_settings_manual)
        #       About
        self.menu_settings_about = QAction("About")
        self.menu_settings_about.setShortcut('Ctrl+Alt+A')
        self.menu_settings_about.setStatusTip('About this Programm')
        self.menu_settings_about.setObjectName("menu_settings_about")
        self.help_menu.addAction(self.menu_settings_about)

    def _left_side(self):
        """
        Init left side objects:
        - Plot canvas
        - Player and settings buttons in layout and frame
        """
        # plot label
        #   Input layout for matplotlib canvas object
        self.verticalLayout_plot_canvas = QVBoxLayout()
        self.verticalLayout_plot_canvas.setObjectName("verticalLayout_plot_canvas")
        self.verticalLayout_left.addLayout(self.verticalLayout_plot_canvas)

        # player button frame and layout
        self.frame_playerbuttons = QFrame()
        self.frame_playerbuttons.setObjectName("frame_playerbuttons")
        self.frame_playerbuttons.setFrameShape(QFrame.StyledPanel)
        self.frame_playerbuttons.setFrameShadow(QFrame.Plain)
        self.frame_playerbuttons.setLineWidth(10)
        self.verticalLayout_left.addWidget(self.frame_playerbuttons)
        self.verticalLayout_playerbottons = QHBoxLayout(self.frame_playerbuttons)
        self.verticalLayout_playerbottons.setObjectName("verticalLayout_playerbottons")

        self._add_player_buttons()

    def _right_side(self):
        """
        Init right side objects:
        - function / method combo boxes with layout and frames
        - function parameter display and button with layout and frame
        - method parameter display and button with layout and frame
        - pseudocode display
        - go and reset button with layput and frame
        """
        # combo boxes frame and layouts
        #   function/method
        self.frame_combo_boxes = QFrame()
        self.frame_combo_boxes.setObjectName("frame_combo_boxes")
        self.frame_combo_boxes.setFrameShape(QFrame.StyledPanel)
        self.frame_combo_boxes.setFrameShadow(QFrame.Plain)
        self.frame_combo_boxes.setLineWidth(10)
        self.frame_combo_boxes.setFixedSize(200, 70)
        self.verticalLayout_right.addWidget(self.frame_combo_boxes)
        self.verticalLayout_combo_boxes = QVBoxLayout(self.frame_combo_boxes)
        self.verticalLayout_combo_boxes.setObjectName("verticalLayout_combo_boxes")
        #   inner combo box frame layouts
        self.horizontalLayout_function = QHBoxLayout()
        self.horizontalLayout_function.setObjectName("horizontalLayout_function")
        self.verticalLayout_combo_boxes.addLayout(self.horizontalLayout_function)
        self.horizontalLayout_method = QHBoxLayout()
        self.horizontalLayout_method.setObjectName("horizontalLayout_method")
        self.verticalLayout_combo_boxes.addLayout(self.horizontalLayout_method)
        #   combo box and label function
        self.label_function = QLabel()
        self.label_function.setObjectName("label_function")
        self.label_function.setText("Function:")
        self.horizontalLayout_function.addWidget(self.label_function)
        self.horizontalLayout_function.setObjectName("label_function")
        self.comboBox_function = QComboBox(self.centralwidget)
        self.comboBox_function.setObjectName("comboBox_function")
        self.comboBox_function.addItem("")
        self.horizontalLayout_function.addWidget(self.comboBox_function)
        #   combo box and label method
        self.label_method = QLabel()
        self.label_function.setObjectName("label_method")
        self.label_method.setText("Method:")
        self.horizontalLayout_method.addWidget(self.label_method)
        self.horizontalLayout_method.setObjectName("horizontalLayout_method")
        self.comboBox_method = QComboBox(self.centralwidget)
        self.comboBox_method.setObjectName("comboBox_method")
        self.comboBox_method.addItem("")
        self.horizontalLayout_method.addWidget(self.comboBox_method)

        # start point
        #   frame and layout
        self.frame_start_point = QFrame()
        self.frame_start_point.setObjectName("frame_start_point")
        self.frame_start_point.setFrameShape(QFrame.StyledPanel)
        self.frame_start_point.setFrameShadow(QFrame.Plain)
        self.frame_start_point.setLineWidth(10)
        self.frame_start_point.setFixedSize(200, 40)
        self.verticalLayout_right.addWidget(self.frame_start_point)
        self.horizontalLayout_start_point = QHBoxLayout(self.frame_start_point)
        self.horizontalLayout_start_point.setObjectName("horizontalLayout_start_point")
        #   button
        self.button_set_start_point = QPushButton()
        self.button_set_start_point.setObjectName("button_set_start_point")
        self.button_set_start_point.setText("Set start point")
        self.horizontalLayout_start_point.addWidget(self.button_set_start_point)
        #   label
        self.label_start_point = QLabel()
        self.label_start_point.setObjectName("label_start_point")
        self.label_start_point.setAlignment(Qt.AlignCenter)
        self.horizontalLayout_start_point.addWidget(self.label_start_point)

        # function parameters
        #   function parameters frame and layout
        self.frame_function_parameters = QFrame()
        self.frame_function_parameters.setObjectName("frame_function_parameters")
        self.frame_function_parameters.setFrameShape(QFrame.StyledPanel)
        self.frame_function_parameters.setFrameShadow(QFrame.Plain)
        self.frame_function_parameters.setLineWidth(10)
        self.frame_function_parameters.setFixedSize(200, 150)
        self.verticalLayout_right.addWidget(self.frame_function_parameters)
        self.verticalLayout_function_parameters = QVBoxLayout(self.frame_function_parameters)
        self.verticalLayout_function_parameters.setObjectName("verticalLayout_function_parameters")
        #   function parameter label
        self.label_function_parameters = QLabel()
        self.label_function_parameters.setObjectName("label_function_parameters")
        self.label_function_parameters.setText("Parameterized function:")
        self.verticalLayout_function_parameters.addWidget(self.label_function_parameters)
        self.label_function_parameters_show = QLabel()
        self.label_function_parameters_show.setObjectName("label_function_parameters_show")
        self.label_function_parameters_show.setFont(self.italic_font)
        self.label_function_parameters_show.setText("    not set yet")
        self.label_function_parameters_show.setFixedHeight(80)
        self.verticalLayout_function_parameters.addWidget(self.label_function_parameters_show)
        #   with scrolling
        self.scroll_area_label_function = QScrollArea()
        self.scroll_area_label_function.setObjectName("scroll_area_label_function")
        self.scroll_area_label_function.setWidgetResizable(True)
        self.scroll_area_label_function.setFixedHeight(80)
        self.scroll_area_label_function.setWidget(self.label_function_parameters_show)
        self.verticalLayout_function_parameters.addWidget(self.scroll_area_label_function)
        #   function parameter button
        self.button_function_parameter = QPushButton()
        self.button_function_parameter.setObjectName("button_function_parameter")
        self.button_function_parameter.setText("Set Parameters")
        self.verticalLayout_function_parameters.addWidget(self.button_function_parameter)

        # method parameters
        #   method parameters frame and layout
        self.frame_method_parameters = QFrame()
        self.frame_method_parameters.setObjectName("frame_method_parameters")
        self.frame_method_parameters.setFrameShape(QFrame.StyledPanel)
        self.frame_method_parameters.setFrameShadow(QFrame.Plain)
        self.frame_method_parameters.setLineWidth(10)
        self.frame_method_parameters.setFixedSize(200, 150)
        self.verticalLayout_right.addWidget(self.frame_method_parameters)
        self.verticalLayout_method_parameters = QVBoxLayout(self.frame_method_parameters)
        self.verticalLayout_method_parameters.setObjectName("verticalLayout_method_parameters")
        #   method parameter label
        self.label_method_parameters = QLabel()
        self.label_method_parameters.setObjectName("label_method_parameters")
        self.label_method_parameters.setText("Method parameters:")
        self.verticalLayout_method_parameters.addWidget(self.label_method_parameters)
        self.label_method_parameters_show = QLabel()
        self.label_method_parameters_show.setObjectName("label_method_parameters_show")
        self.label_method_parameters_show.setFont(self.italic_font)
        self.label_method_parameters_show.setText("    not set yet")
        self.label_method_parameters_show.setFixedHeight(80)
        self.verticalLayout_method_parameters.addWidget(self.label_method_parameters_show)
        #   with scrolling
        self.scroll_area_label_method = QScrollArea()
        self.scroll_area_label_method.setObjectName("scroll_area_label_method")
        self.scroll_area_label_method.setWidgetResizable(True)
        self.scroll_area_label_method.setFixedHeight(80)
        self.scroll_area_label_method.setWidget(self.label_method_parameters_show)
        self.verticalLayout_method_parameters.addWidget(self.scroll_area_label_method)
        #   method parameter button
        self.button_method_parameter = QPushButton()
        self.button_method_parameter.setObjectName("button_method_parameter")
        self.button_method_parameter.setText("Set Parameters")
        self.verticalLayout_method_parameters.addWidget(self.button_method_parameter)

        # pseudocode
        self.label_animation_pseudocode = PseudocodeHighlightAnimation()
        self.label_animation_pseudocode.setObjectName("label_animation_pseudocode")
        self.verticalLayout_right.addWidget(self.label_animation_pseudocode)

        # show and reset button frame and layout
        self.frame_show_reset = QFrame()
        self.frame_show_reset.setObjectName("frame_show_reset")
        self.frame_show_reset.setFrameShape(QFrame.StyledPanel)
        self.frame_show_reset.setFrameShadow(QFrame.Plain)
        self.frame_show_reset.setLineWidth(10)
        self.frame_show_reset.setFixedSize(200, 90)
        self.verticalLayout_right.addWidget(self.frame_show_reset)
        self.verticalLayout_show_reset = QVBoxLayout(self.frame_show_reset)
        self.verticalLayout_show_reset.setObjectName("verticalLayout_show_reset")
        #   show button
        self.button_calculate = QPushButton()
        self.button_calculate.setObjectName("button_calculate")
        self.verticalLayout_show_reset.addWidget(self.button_calculate)
        self.button_calculate.setText('Calculate')
        #   reset button
        self.button_reset = QPushButton()
        self.button_reset.setObjectName("button_reset")
        self.verticalLayout_show_reset.addWidget(self.button_reset)
        self.button_reset.setText('Reset')

    def _add_player_buttons(self):
        """
        Init 'media' player buttons as well as all other buttons in this frame
        """
        # player buttons size policy
        self.button_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        # first button
        self.button_first = QPushButton(self.centralwidget)
        self.button_first.setObjectName("button_first")
        self.first_icon = QIcon(module_dir + 'gui_imgs/first.png')
        self.button_first.setIcon(self.first_icon)
        self.button_first.setIconSize(QSize(35, 35))
        self.button_first.setFlat(True)
        self.verticalLayout_playerbottons.addWidget(self.button_first, alignment=Qt.AlignRight)

        # previous button
        self.button_prev = QPushButton(self.centralwidget)
        self.button_prev.setObjectName("button_prev")
        self.prev_icon = QIcon(module_dir + 'gui_imgs/prev.png')
        self.button_prev.setIcon(self.prev_icon)
        self.button_prev.setIconSize(QSize(50, 50))
        self.button_prev.setFlat(True)
        self.verticalLayout_playerbottons.addWidget(self.button_prev, alignment=Qt.AlignLeft)

        # play / pause button
        self.button_play_pause = QPushButton(self.centralwidget)
        self.button_play_pause.setObjectName("button_play_pause")
        self.button_play_pause_icon = QIcon(module_dir + 'gui_imgs/play.png')
        self.button_play_pause.setIcon(self.button_play_pause_icon)
        self.button_play_pause.setIconSize(QSize(55, 55))
        self.button_play_pause.setFlat(True)
        self.verticalLayout_playerbottons.addWidget(self.button_play_pause, alignment=Qt.AlignCenter)

        # next button
        self.button_next = QPushButton(self.centralwidget)
        self.button_next.setObjectName("button_next")
        self.next_icon = QIcon(module_dir + 'gui_imgs/next.png')
        self.button_next.setIcon(self.next_icon)
        self.button_next.setIconSize(QSize(50, 50))
        self.button_next.setFlat(True)
        self.verticalLayout_playerbottons.addWidget(self.button_next, alignment=Qt.AlignRight)

        # last button
        self.button_last = QPushButton(self.centralwidget)
        self.button_last.setObjectName("button_last")
        self.last_icon = QIcon(module_dir + 'gui_imgs/last.png')
        self.button_last.setIcon(self.last_icon)
        self.button_last.setIconSize(QSize(35, 35))
        self.button_last.setFlat(True)
        self.verticalLayout_playerbottons.addWidget(self.button_last, alignment=Qt.AlignLeft)

        # array position and xy mouse coords
        self.verticalLayout_pos_xy = QVBoxLayout()
        self.verticalLayout_pos_xy.setObjectName("verticalLayout_pos_xy")
        self.verticalLayout_playerbottons.addLayout(self.verticalLayout_pos_xy)
        #   array position
        self.horizontalLayout_array_position = QHBoxLayout()
        self.horizontalLayout_array_position.setObjectName("horizontalLayout_startpoint")
        self.horizontalLayout_array_position.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.verticalLayout_pos_xy.addLayout(self.horizontalLayout_array_position)
        #   array position spinbox
        self.spinbox_currentposition = QSpinBox()
        self.spinbox_currentposition.setObjectName("spinbox_currentposition")
        self.spinbox_currentposition.setValue(0)
        self.spinbox_currentposition.setMaximum(0)
        self.horizontalLayout_array_position.addWidget(self.spinbox_currentposition)
        #   array length lable
        self.label_arraylength = QLabel()
        self.label_arraylength.setObjectName("label_arraylength")
        self.label_arraylength.setText("/ -")
        self.horizontalLayout_array_position.addWidget(self.label_arraylength)
        #   xy cords
        self.label_xy = QLabel()
        self.label_xy.setObjectName("label_xy")
        self.label_xy.setText("x: | y:")
        self.verticalLayout_pos_xy.addWidget(self.label_xy)

        # speed control
        self.verticalLayout_speed = QVBoxLayout()
        self.verticalLayout_playerbottons.addLayout(self.verticalLayout_speed)
        #   slow fast label
        self.label_speed = QLabel()
        self.label_speed.setText("slow             fast")
        self.label_speed.setAlignment(Qt.AlignBottom)
        self.verticalLayout_speed.addWidget(self.label_speed)
        #   slider
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setObjectName("slider_speed")
        self.slider_speed.setTickInterval(25)
        self.slider_speed.setFixedSize(75, 20)
        self.slider_speed.setSingleStep(1)
        self.slider_speed.setValue(50)
        self.slider_speed.setTickPosition(QSlider.NoTicks)
        self.verticalLayout_speed.addWidget(self.slider_speed)

    def _presets(self, MainWindow):
        """
        Helper variables to be used in object inits
        :param MainWindow: MainWindow object. see main.py and guis_event_handler.py for further information
        """
        self.italic_font = QFont()
        self.italic_font.setItalic(True)
        self.non_italic_font = QFont()
        self.non_italic_font.setItalic(False)

        self.MainWindow = MainWindow

    def _postsets(self):
        """
        No Idea what this is doing
        """
        self.MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(self.MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.MainWindow.setStatusBar(self.statusbar)
        QMetaObject.connectSlotsByName(self.MainWindow)

    def set_pseudocode(self, pseudocode_pos):
        """
        Sets the pseudo code picture anew
        :param pseudocode_pos: current pseudo code line number
        """
        self.label_animation_pseudocode.move(pseudocode_pos)
