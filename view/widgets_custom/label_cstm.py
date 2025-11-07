from PySide2.QtGui import QFont
from PySide2.QtWidgets import QLabel
from PySide2.QtCore import QTimer, Qt
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root)) 

class labelCustom(QLabel):
    def __init__(self, text , parent=None):
        super(labelCustom, self).__init__(text, parent)

    def heading(self, key = None):
        self.set_label(marge=10, font="Reem Kufi", size=16, weight=QFont.Bold, key = key)

    def subheading(self, key = None):
        self.set_label(marge=8, font="Bahnschrift SemiBold", size=12, weight=QFont.Medium, key = key)

    def listFormat(self, key = None):
        self.set_label(marge=0, font="Arial", size=10, weight=QFont.Medium, key = key)

    def body_text(self, key = None):
        self.set_label(marge=5, font="Arial", size=8, weight=QFont.Normal, key = key)

    def set_label(self, marge:int=None, font:str=None, size:int=None, weight:int=None, italic:bool=None, key = None):
        if marge is not None:
            current_stylesheet = self.styleSheet()
            self.setStyleSheet(current_stylesheet + f"margin: {marge}px;")

        # Créer un objet QFont avec les paramètres spécifiés
        current_font = self.font()  # Obtenir la police actuelle pour ne pas écraser les propriétés non modifiées
        if font:
            current_font.setFamily(font)
        if size:
            current_font.setPointSize(size)
        if weight:
            current_font.setWeight(weight)
        if italic is not None:
            current_font.setItalic(italic)

        self.setFont(current_font)




