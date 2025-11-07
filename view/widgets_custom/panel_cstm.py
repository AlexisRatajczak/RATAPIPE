from PySide2.QtWidgets import QFrame, QSizePolicy
from PySide2.QtCore import QPropertyAnimation, QEasingCurve

class panelCustom(QFrame):
    def __init__(self, parent=None):
        super(panelCustom, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setContentsMargins(10, 0, 10, 0)
        self.setMinimumWidth(0)  # Taille minimale de 0
        self.setProperty("open", False)  # Le panneau est initialement fermé

        # Commencez sans largeur fixe, ce qui évite les problèmes de taille négative
        self.setMaximumWidth(0)  # Ajustez la largeur maximale à 0 pour un état "fermé"

    def toggle_menu_panel(self):
        if self.property("open"):
            self.animate_menu(350, 0, QEasingCurve.InOutQuart)  # Fermer le panneau
        else:
            self.animate_menu(350, 250, QEasingCurve.InOutQuart )  # Ouvrir le panneau
        self.setProperty("open", not self.property("open"))

    def animate_menu(self, duration, width, animation):
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(width)
        self.animation.setEasingCurve(animation)  # Remplacez par OutQuad ou un autre selon votre goût
        self.animation.start()