from PySide2.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFileDialog
from PySide2.QtCore import Qt 
import sys
from pathlib import Path
import re

project_root = Path(__file__).resolve().parents[1] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root)) 

from view.widgets_custom import panel_cstm, pushButton_cstm, textField_cstm, label_cstm, colorDialog_cstm
from common import set_data, user_cmds

class taskbar(QWidget):
    def __init__(self, parent = None):
        super(taskbar, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.pipePanel = panel_cstm.panelCustom()
        self.pipeW = pipeSetWidget(self.pipePanel)
        self.pipeButton = pushButton_cstm.pushButtonCustom()
        self.pipeButton.set_button(size=(64, 64), icon=None, connect=self.toggle_pipe_panel)

        # Initialize panels and buttons
        self.userPanel = panel_cstm.panelCustom()
        self.userW = userWidget( self.userPanel)
        self.userButton = pushButton_cstm.pushButtonCustom()
        self.userButton.set_button(size=(64, 64), icon=None, connect=self.toggle_user_panel)

        # Frame and layout for buttons
        self.buttonsWidget = QFrame()
        self.buttonsWidget.setFixedWidth(66)
        self.buttonsWidget.setFrameShape(QFrame.StyledPanel)

        self.buttonsLayout = QVBoxLayout(self.buttonsWidget)
        self.buttonsLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.buttonsLayout.setAlignment(Qt.AlignTop)
        self.buttonsLayout.addWidget(self.pipeButton)
        self.buttonsLayout.addWidget(self.userButton)

        # General layout
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins from main layout
        self.mainLayout.setAlignment(Qt.AlignLeft)
        self.mainLayout.addWidget(self.buttonsWidget)
        self.mainLayout.addWidget(self.pipePanel)
        self.mainLayout.addWidget(self.userPanel)
        self.setLayout(self.mainLayout)

    def toggle_pipe_panel (self):
        self.pipePanel.toggle_menu_panel()
        if self.userPanel.property("open"):
            self.userPanel.toggle_menu_panel()

    def toggle_user_panel (self):
        self.userPanel.toggle_menu_panel()
        if self.pipePanel.property("open"):
            self.pipePanel.toggle_menu_panel()

class pipeSetWidget(QWidget):
    def __init__(self, parent = None):
        super(pipeSetWidget, self).__init__(parent)
        self.init_ui()
        self.set_root_path()

    def init_ui(self):

        #set widgets

        self.menu_text = label_cstm.labelCustom('Home')
        self.menu_text.heading(key = 'color1')

        label_pipe = label_cstm.labelCustom('Pipeline path:')
        label_pipe.subheading()

        self.path_pipe_button = pushButton_cstm.pushButtonCustom("Select the folder", size = (100,26))
        self.path_pipe_button.clicked.connect(self.open_folder_dialog)
        self.path_pipe_button.clicked.connect(self.update_path_connect)
        
        self.update_path_button = pushButton_cstm.pushButtonCustom("Set New Path", size = (100,26))

        self.path_pipe_field = QLineEdit()
        self.path_pipe_field.setFixedWidth(240)
        self.path_pipe_field.setReadOnly(True)

        #Layout

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.addWidget(self.path_pipe_button)
        self.buttonsLayout.addWidget(self.update_path_button)
        
        self.pipe_layout = QVBoxLayout()
        self.pipe_layout.addWidget(label_pipe, alignment=Qt.AlignTop)
        self.pipe_layout.addLayout(self.buttonsLayout)
        self.pipe_layout.addWidget(self.path_pipe_field)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.mainLayout.addWidget(self.menu_text, alignment=Qt.AlignTop)
        self.mainLayout.addLayout(self.pipe_layout)
        self.setLayout(self.mainLayout)

    def set_root_path(self, root_path:Path = None):
        if root_path:
            self.path_pipe_field.setPlaceholderText(root_path)
        else:
            self.path_pipe_field.setPlaceholderText("Chemin du dossier")

    def update_path_connect(self, connect:callable = None):
        if connect:
            self.update_path_button.clicked.connect(connect)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(None, "Sélectionner un Dossier")
        if folder:
            self.path_pipe_field.setText(folder)

            relative_path = "config/pipeline_data.json"
            
            # Utilisation du chemin relatif
            handler = set_data.JsonHandler(relative_path)

            handler.update_item(f"{'path'}", folder)
        return folder

class userWidget(QWidget):
    def __init__(self, parent = None):
        super(userWidget, self).__init__(parent)
        relative_path = "config/colors.json"
        handler = set_data.JsonHandler(relative_path)
        self.color_data = handler.read_json()

        self.init_ui()

    def init_ui(self):
        self.mainLayout = QVBoxLayout(self)

        self.menu_text = label_cstm.labelCustom('Color')
        self.menu_text.heading(key = 'color1')

        # Define color buttons
        self.colorButton1 = pushButton_cstm.pushButtonCustom(size = (64,20), connect=lambda: self.open_color_dialog(self.colorButton1, key='color1'))
        self.colorButton2 = pushButton_cstm.pushButtonCustom(size = (64,20), connect=lambda: self.open_color_dialog(self.colorButton2, key='color2'))
        self.colorButton3 = pushButton_cstm.pushButtonCustom(size = (64,20), connect=lambda: self.open_color_dialog(self.colorButton3, key='color3'))
        #self.colorButton4 = pushButton_cstm.pushButtonCustom(size = (64,20), connect=lambda: self.open_color_dialog(self.colorButton4, key='color4'))
        #self.colorButton5 = pushButton_cstm.pushButtonCustom(size = (64,20), connect=lambda: self.open_color_dialog(self.colorButton5, key='color5'))

        # Set initial button colors based on stored color data
        for key, button in zip(['color1', 'color2', 'color3'], 
                               [self.colorButton1, self.colorButton2, self.colorButton3]):
            if key in self.color_data:
                button.setStyleSheet(f"background-color: {self.color_data[key]}; border: 1px solid {self.color_data['color1']};")

        # Add widgets to layout
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.mainLayout.addWidget(self.menu_text)
        self.mainLayout.addWidget(self.colorButton1)
        self.mainLayout.addWidget(self.colorButton2)
        self.mainLayout.addWidget(self.colorButton3)
        #self.mainLayout.addWidget(self.colorButton4)
        #self.mainLayout.addWidget(self.colorButton5)

        self.setLayout(self.mainLayout)

    def open_color_dialog(self, button, key):
        dialog = colorDialog_cstm.ColorDialogCustom()
        color = dialog.get_color()

        if color:
            name = color.name()
            button.setStyleSheet(f"background-color: {name};")

            relative_path = "config/colors.json"
            handler = set_data.JsonHandler(relative_path)

            handler.update_item(key, name)

            # Update border color of all color buttons
            for button in [self.colorButton1, self.colorButton2, self.colorButton3]:
                ss = button.styleSheet()
                ss = re.sub(r"border:\s*\d+px\s*solid\s*[^;]+;", f"border: 1px solid {self.color_data['color1']};", ss)
                button.setStyleSheet(ss)
