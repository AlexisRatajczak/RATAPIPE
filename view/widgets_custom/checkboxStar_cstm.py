from PySide2.QtCore import QPoint, Qt
from PySide2.QtGui import QPainter, QBrush, QColor, QPen, QPolygon
from PySide2.QtWidgets import QCheckBox

class starCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super(starCheckBox, self).__init__(parent)
        self.setMinimumSize(44, 44)  # Taille minimale ajustée (un peu plus grande que 22x22 pour laisser de l'espace)
        self.setChecked(False)  # Initialement décochée
        self.star_polygon = self.create_star_polygon()  # Créer l'étoile

    def create_star_polygon(self):
        """Crée et retourne un QPolygon représentant une étoile de 22 px de large"""
        points = [
            QPoint(11, 2),   QPoint(13, 9),  QPoint(20, 9),
            QPoint(15, 13),  QPoint(17, 20),  QPoint(11, 16),
            QPoint(5, 20),   QPoint(7, 13),  QPoint(2, 9),
            QPoint(9, 9)
        ]
        return QPolygon(points)

    def paintEvent(self, event):
        """Dessine l'étoile en fonction de l'état (coché/décoché)"""

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Définir la couleur de remplissage selon l'état coché/décoché
        if self.isChecked():
            painter.setBrush(QBrush(QColor("#FFD700")))  # Bleu clair si coché
            painter.setPen(QPen(QColor("#FFD700"), 2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))  # Pas de remplissage si décoché
            painter.setPen(QPen(QColor("#87CEEB"), 2))
        # Dessiner l'étoile avec un contour bleu clair  # Bordure bleu clair
        painter.drawPolygon(self.star_polygon)

    def mousePressEvent(self, event):
        """Gère les clics de souris sur la zone de l'étoile uniquement"""
        if self.star_polygon.containsPoint(event.pos(), Qt.OddEvenFill):
            # Inverser l'état de la checkbox si le clic est dans l'étoile
            self.setChecked(not self.isChecked())
            self.update()  # Redessiner la checkbox pour mettre à jour l'affichage
        else:
            super().mousePressEvent(event)

    def sizeHint(self):
        """Taille suggérée pour la checkbox"""
        return self.minimumSizeHint()