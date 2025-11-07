from PySide2.QtWidgets import QWidget, QLineEdit, QCheckBox, QHBoxLayout

class textFieldCustom(QWidget):
    def __init__(self, parent=None, text = "specific name"):
        super(textFieldCustom, self).__init__(parent)
        self.text = text
        self.init_ui()

    def init_ui(self):
        self.mainWidget = QWidget()
        # Création des widgets
        self.text_field = QLineEdit(self)  # Champ de texte
        self.checkbox = QCheckBox(self)  # Case à cocher

        # Par défaut, le champ de texte est désactivé
        self.text_field.setEnabled(False)
        self.text_field.setText(self.text)

        # Connecter la case à cocher à la méthode qui active/désactive le champ de texte
        self.checkbox.stateChanged.connect(self.activation_text_field)

        # Disposition verticale
        layout = QHBoxLayout(self.mainWidget)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_field)

        self.setLayout(layout)

    def activation_text_field(self, state):
        """Active ou désactive le champ de texte en fonction de la case à cocher."""
        if state == 2:  # 2 correspond à l'état "Checked" (coché)
            self.text_field.setEnabled(True)
        else:
            self.text_field.setEnabled(False)