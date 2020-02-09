"""
PopUp GUI submodule.

includes classes for Notification/Warning pop up messages
"""


########### IMPORTS ###########
# <editor-fold desc="Open">

# packages
from abc import ABCMeta, abstractmethod
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QListWidget

# files from gui
from .helpful_stuff import module_dir
from .latex import detect_latex_in_string

# </editor-fold>
########### IMPORTS ###########


class PopUpInfo(QDialog):
    """
    Abstract Base Class, inherting from QDialog,
    extended by Warning and Notification popup
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, text):
        """
        init
        :param text: info text in main window of popup
        """
        super(PopUpInfo, self).__init__()

        # call gui building functions
        self._create_main_layout()
        self._create_text_label(text)
        self._create_buttons()

    def _create_main_layout(self):
        """
        Presets and main layout
        """
        self.verticalLayout_warning = QVBoxLayout()
        self.verticalLayout_warning.setObjectName("verticalLayout_warning")
        self.setLayout(self.verticalLayout_warning)

    def _create_text_label(self, text):
        """
        creates main message label from
        :param text: string or list of strings
        """
        if isinstance(text, str):
            # text label
            self.label_Warning = QLabel()
            self.label_Warning.setObjectName("label_Warning")
            # set text
            text, latex_bool = detect_latex_in_string(text)
            if latex_bool:  # either way pixmap from latex
                self.label_Warning.setPixmap(text)
            else:  # or plain text
                self.label_Warning.setText(text)
            self.label_Warning.setAlignment(Qt.AlignCenter)
            self.verticalLayout_warning.addWidget(self.label_Warning)
        elif isinstance(text, list):
            self.list_warning = QListWidget()
            self.list_warning.addItems(text)
            self.verticalLayout_warning.addWidget(self.list_warning)

    def _create_buttons(self):
        """
        OK / cancel buttons
        """
        self.buttons_okcancel = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox_okcancel = QDialogButtonBox(self.buttons_okcancel)
        self.buttonBox_okcancel.setObjectName("buttonBox_Warning")
        self.buttonBox_okcancel.accepted.connect(self.accept)
        self.buttonBox_okcancel.rejected.connect(self.reject)
        self.verticalLayout_warning.addWidget(self.buttonBox_okcancel)


class PopUpWarning(PopUpInfo):
    """
    Warning PopUp with input text
    """

    def __init__(self, text):
        """
        init
        :param text: warning message text
        """
        super(PopUpWarning, self).__init__(text)

        # Setting Popup specific message and deco
        self.icon_warning = QIcon(module_dir + "gui_imgs/warning.png")
        self.setWindowIcon(self.icon_warning)
        self.setWindowTitle("Warning")


class PopUpNotification(PopUpInfo):
    """
    Warning PopUp with input text
    """
    def __init__(self, text):
        """
        init
        :param text: notification message text
        """
        super(PopUpNotification, self).__init__(text)

        # Setting Popup specific message and deco
        self.setWindowTitle("Notification")
        self.icon_warning = QIcon(module_dir + "gui_imgs/info.png")
        self.setWindowIcon(self.icon_warning)