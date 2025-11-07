from PySide2.QtWidgets import QPushButton
from PySide2.QtGui import QIcon
from PySide2.QtCore import QSize
from pathlib import Path

class pushButtonCustom(QPushButton):
    def __init__(self, parent=None, size: tuple[int, int] = (64, 64), icon: Path = None, connect: callable = None):
        super(pushButtonCustom, self).__init__(parent)
        self.set_button(size = size, icon = icon, connect = connect)

    def set_button(self, size: tuple[int, int] = (64, 64), icon: Path = None, connect: callable = None):
        self.setFixedSize(size[0], size[1])  # Set button size
        if icon:
            self.setIcon(QIcon(icon))  # Set icon if provided
            self.setIconSize(QSize(size[0], size[1]))  # Set icon size
        if connect and callable(connect):  # Ensure connect is callable
            self.clicked.connect(connect)
        
