from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidgetItem, QHeaderView, QMessageBox, QApplication
from PySide2.QtGui import QClipboard

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from view.widgets_custom import contextMenu_cstm
from view.view_common import formatData_file

class ScenesTableWidget(QTableWidget):  # Changer QTableWidget à QWidget ici
    def __init__(self, root_path, on_change_callback=None, parent=None):
        super(ScenesTableWidget, self).__init__(parent)
        self.root_path = root_path
        self.on_change_callback = on_change_callback
        self.selected_folder_path = ""
        self.scene_name = ""
        self.file_path = ""
        self.init_ui()

    def init_ui(self):
        # Créer un QLabel pour afficher le chemin complet du dossier + spe + publish
        self.full_path_label = QLabel("Path : ")
        self.full_path_label.setToolTip("Cliquez pour copier le chemin")
        self.full_path_label.mousePressEvent = self.copy_root_path_to_clipboard  # Connecter le clic pour copier

        # Ajouter un bouton pour ouvrir l'explorateur de fichiers
        self.open_button = QPushButton("")
        self.open_button.setMaximumWidth(10)
        self.open_button.clicked.connect(self.open_root_path_in_explorer)  # Connecter le bouton pour ouvrir

        # Layout horizontal pour le label et le bouton
        pathLayout = QHBoxLayout()
        pathLayout.addWidget(self.full_path_label)
        pathLayout.addWidget(self.open_button)

        # Créer un QTableWidget pour afficher les scènes
        self.scenes_list_tableWidget = QTableWidget()
        self.scenes_list_tableWidget.setColumnCount(3)
        self.scenes_list_tableWidget.setHorizontalHeaderLabels(['Name', 'Date', 'Size'])
        self.scenes_list_tableWidget.verticalHeader().setVisible(False)
        self.scenes_list_tableWidget.setShowGrid(False)
        self.scenes_list_tableWidget.setSelectionBehavior(QTableWidget.SelectRows)

        # Configurer les modes de redimensionnement des colonnes
        header = self.scenes_list_tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        # Fixer la largeur de la colonne Taille (colonne 2) à 70 px
        self.scenes_list_tableWidget.setColumnWidth(2, 70)
        self.scenes_list_tableWidget.setColumnWidth(1, 100)
        self.scenes_list_tableWidget.itemClicked.connect(self.on_scene_item_clicked)

        # Layout principal
        scenesListLayout = QVBoxLayout(self)
        scenesListLayout.addLayout(pathLayout)  # Ajouter le layout du chemin avec le bouton
        scenesListLayout.addWidget(self.scenes_list_tableWidget)

        self.setLayout(scenesListLayout)

        # Menu contextuel
        self.contextMenu = contextMenu_cstm.contextMenu(self.scenes_list_tableWidget, self.root_path)
        self.contextMenu.add_action("rename", self.contextMenu.rename_scene)
        self.contextMenu.add_action("copy path", self.contextMenu.copy_path)
        self.contextMenu.add_action("open in file explorer", self.contextMenu.open_in_explorer)

        self.scenes_list_tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenes_list_tableWidget.customContextMenuRequested.connect(self.contextMenu.show_context_menu)


    def copy_root_path_to_clipboard(self, event):
        """Copie root_path dans le presse-papiers lorsque le label est cliqué."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.root_path)
        print(f"{self.root_path} a été copié dans le presse-papiers.")

    def open_root_path_in_explorer(self):
        """Ouvre le root_path dans l'explorateur de fichiers."""
        try:
            os.startfile(self.root_path)  # Ouvrir l'explorateur de fichiers sur Windows
            print(f"{self.root_path} a été ouvert dans l'explorateur de fichiers.")
        except Exception as e:
            print(f"Erreur lors de l'ouverture de {self.root_path} dans l'explorateur de fichiers: {e}")

    def paste_item(self):
        # Coller le texte du presse-papiers comme un nouvel élément dans la liste
        text = self.clipboard.text()
        if text:
            self.addItem(text)
            QMessageBox.information(self, "Information", "Collé : " + text)
    def on_scene_item_clicked(self, item):
        # Récupérer le texte de l'élément sélectionné
        self.data_item = item.data(Qt.UserRole)
        self.file_path = self.data_item["full_path"]
        self.on_change_callback()
        
    def update_scenes_list(self, folder_path):
        """Met à jour le QTableWidget des scènes avec les fichiers du dossier sélectionné."""
        self.scenes_list_tableWidget.setRowCount(0)  # Vider la liste avant de la remplir
        #try:
            # Récupérer la liste des fichiers dans le dossier
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))][::-1]
        # Définir le nombre de lignes en fonction du nombre de fichiers
        self.scenes_list_tableWidget.setRowCount(len(files))

        # Parcourir les fichiers et ajouter leurs informations
        for row, item_name in enumerate(files):
            full_path = os.path.join(folder_path, item_name)
            format_file = formatData_file.FormatDataFile(os.path.join(full_path))
            name, extension = os.path.splitext(item_name)
            # Formatage de la date et de la taille
            date = format_file.format_date()
            size = format_file.format_size()

            # Ajouter les informations dans les colonnes du QTableWidget
            self.scenes_list_tableWidget.setItem(row, 0, QTableWidgetItem(name+extension))  # Colonne Nom
            self.scenes_list_tableWidget.setItem(row, 1, QTableWidgetItem(date))  # Colonne Date
            self.scenes_list_tableWidget.setItem(row, 2, QTableWidgetItem(size))  # Colonne Taille

            # Aligner la taille à droite
            self.scenes_list_tableWidget.item(row, 2).setTextAlignment(Qt.AlignRight)

            # Stocker le chemin complet dans une propriété de l'élément (si nécessaire)
            data={"full_path": full_path,
                  "path": folder_path,
                    "name": name,
                    "extension": extension,
                    "date": date,
                    "size": size}
            for column in range(self.scenes_list_tableWidget.columnCount()):
                self.scenes_list_tableWidget.item(row, column).setData(Qt.UserRole, data)
        

        #except Exception as e:
        #    print(f"Erreur lors de la mise à jour de la liste des scènes : {e}")