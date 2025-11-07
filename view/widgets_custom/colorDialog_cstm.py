from PySide2.QtWidgets import QWidget, QLineEdit, QCheckBox, QHBoxLayout

from PySide2.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit, QPushButton, QFrame, QWidget
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QColor, QPalette, QPixmap, QPainter
import sys

class ColorPickerMap(QFrame):
    def __init__(self, callback, value=255):
        super().__init__()
        self.callback = callback
        self.value = value  # Valeur (luminosité)
        self.color = QColor(255, 0, 0)  # Couleur initiale (rouge)
        self.setFixedSize(200, 200)  # Taille de la carte de couleur
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

    def paintEvent(self, event):
        # Crée un dégradé pour la carte de couleurs, ajustée selon la luminosité (value)
        pixmap = QPixmap(self.size())
        painter = QPainter(pixmap)

        for x in range(self.width()):
            for y in range(self.height()):
                hue = x / self.width() * 360  # Teinte (hue)
                saturation = y / self.height() * 255  # Saturation
                color = QColor.fromHsv(int(hue), int(saturation), self.value)
                painter.setPen(color)
                painter.drawPoint(QPoint(x, y))

        painter.end()
        painter.begin(self)
        painter.drawPixmap(0, 0, pixmap)

        # Dessine le curseur (point) à la position de la couleur sélectionnée
        hue_pos = self.color.hue() / 360 * self.width()
        sat_pos = self.color.saturation() / 255 * self.height()

        painter.setPen(Qt.red)  # Couleur du curseur (rouge)
        painter.setBrush(Qt.red)
        painter.drawEllipse(hue_pos - 5, sat_pos - 5, 10, 10)  # Dessine un petit cercle comme curseur

        painter.end()

    def mousePressEvent(self, event):
        self.select_color_at(event.pos())  # Sélectionne la couleur à la position de la souris

    def mouseMoveEvent(self, event):
        self.select_color_at(event.pos())  # Sélectionne la couleur lorsque la souris se déplace

    def select_color_at(self, pos):
        # Calcule la couleur en fonction de la position de la souris sur la carte
        if 0 <= pos.x() < self.width() and 0 <= pos.y() < self.height():
            hue = pos.x() / self.width() * 360
            saturation = pos.y() / self.height() * 255
            self.color.setHsv(int(hue), int(saturation), self.value)
            self.callback(self.color)  # Met à jour la couleur sélectionnée

    def set_value(self, value):
        self.value = value  # Mise à jour de la luminosité (value)
        self.update()  # Redessine la carte de couleur


class ColorDialogCustom(QDialog):
    def __init__(self):
        super().__init__()

        # Configuration de la boîte de dialogue
        self.setWindowTitle("Sélecteur de Couleur Avancé")
        self.setFixedSize(400, 450)

        # Couleur initiale
        self.color = QColor(255, 0, 0)  # Couleur initiale (rouge)

        # Carte de couleur
        self.color_map = ColorPickerMap(self.on_color_selected)

        # Curseurs RGB
        self.red_slider = self.create_slider(255, "Rouge", self.update_color_from_rgb)
        self.green_slider = self.create_slider(0, "Vert", self.update_color_from_rgb)
        self.blue_slider = self.create_slider(0, "Bleu", self.update_color_from_rgb)

        # Curseur pour la luminosité (Valeur)
        self.value_slider = self.create_slider(255, "Valeur", self.update_color_from_value)

        # Entrée hexadécimale
        self.hex_input = QLineEdit("#ff0000")
        self.hex_input.setAlignment(Qt.AlignCenter)
        self.hex_input.textChanged.connect(self.on_hex_changed)

        # Prévisualisation
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(100, 100)
        self.update_preview()

        # Bouton de validation
        self.ok_button = QPushButton("Appliquer")
        self.ok_button.clicked.connect(self.accept)

        # Mise en page
        main_layout = QVBoxLayout()

        # Layout de la carte de couleur et des sliders
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.color_map)
        sliders_layout = QVBoxLayout()
        sliders_layout.addWidget(self.red_slider)
        sliders_layout.addWidget(self.green_slider)
        sliders_layout.addWidget(self.blue_slider)
        sliders_layout.addWidget(self.value_slider)
        color_layout.addLayout(sliders_layout)

        # Ajout des éléments au layout principal
        main_layout.addLayout(color_layout)
        main_layout.addWidget(self.preview_label)
        main_layout.addWidget(QLabel("Code Hexadécimal :"))
        main_layout.addWidget(self.hex_input)
        main_layout.addWidget(self.ok_button)
        self.setLayout(main_layout)

        self.setStyleSheet(self.get_stylesheet())

    def create_slider(self, initial_value, label, callback):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 255)
        slider.setValue(initial_value)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(5)
        slider_label = QLabel(f"{label}: {initial_value}")
        slider.valueChanged.connect(lambda value, label=label: callback(value, label))
        return slider

    def update_color_from_rgb(self, value, label):
        if label == "Rouge":
            self.color.setRed(value)
        elif label == "Vert":
            self.color.setGreen(value)
        elif label == "Bleu":
            self.color.setBlue(value)

        # Met à jour la carte de couleur et la prévisualisation
        self.update_preview()
        self.update_hex_input()

    def update_color_from_value(self, value, label):
        if label == "Valeur":
            # Mise à jour de la couleur HSV (teinte et saturation inchangées)
            self.color.setHsv(self.color.hue(), self.color.saturation(), value)
            self.color_map.set_value(value)  # Mise à jour de la carte de couleur

        # Met à jour la prévisualisation
        self.update_preview()
        self.update_hex_input()

    def on_color_selected(self, color):
        self.color = color
        self.red_slider.setValue(self.color.red())
        self.green_slider.setValue(self.color.green())
        self.blue_slider.setValue(self.color.blue())
        self.value_slider.setValue(self.color.value())
        self.update_preview()
        self.update_hex_input()

    def update_preview(self):
        # Met à jour la prévisualisation de la couleur
        palette = self.preview_label.palette()
        palette.setColor(QPalette.Window, self.color)
        self.preview_label.setAutoFillBackground(True)
        self.preview_label.setPalette(palette)

    def update_hex_input(self):
        # Met à jour le champ hexadécimal
        self.hex_input.setText(self.color.name())

    def on_hex_changed(self):
        hex_code = self.hex_input.text()
        if QColor.isValidColor(hex_code):
            self.color.setNamedColor(hex_code)
            self.red_slider.setValue(self.color.red())
            self.green_slider.setValue(self.color.green())
            self.blue_slider.setValue(self.color.blue())
            self.value_slider.setValue(self.color.value())
            self.update_preview()

    def get_stylesheet(self):
        return """
            QDialog {
                background-color: #2E3440;
                color: #D8DEE9;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel, QLineEdit {
                color: #ECEFF4;
                font-size: 12px;
            }
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QSlider::groove:horizontal {
                background: #4C566A;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #88C0D0;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """

    def get_color(self):
        return self.color if self.exec_() == QDialog.Accepted else None