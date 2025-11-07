from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QLineEdit, QListWidget
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt

import os
import shutil
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from view.widgets_custom import label_cstm, list_cstm
from common import set_data


class AddDirectoryWindow(QWidget):
    def __init__(self, directory, directory_copy, on_change_callback):
        super().__init__()
        self.directory = directory
        self.directory_copy = directory_copy
        self.path_directory_copy = os.path.join(self.directory+"/" + self.directory_copy)
        self.on_change_callback=on_change_callback
        self.image_path = ''

        self.SPECIALITY = {}

        for item_name in os.listdir(directory):
            full_path = os.path.join(directory, item_name)
            if os.path.isdir(full_path): 
                if '_' not in item_name[0]:
                    self.SPECIALITY[item_name] = full_path

        self.setWindowTitle("Sous-fenêtre - Add Directory")
        self.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout()
        label = QLabel("Ceci est une sous-fenêtre ADD")

        label_name = label_cstm.labelCustom('Enter the name of the new directory:')
        label_name.body_text()
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Name")


        self.speSelectionW = list_cstm.listWidget(self.SPECIALITY, minWidth=140, maxWidth=260)

        add_button = QPushButton('add')
        add_button.clicked.connect(self.add_asset)

        layout_name = QVBoxLayout()
        layout_name.addWidget(label_name)
        layout_name.addWidget(self.name_field)
        layout_name.addWidget(self.speSelectionW)
        layout_name.addWidget(add_button)
        
        layout.addWidget(label)
        layout.addLayout(layout_name)
        self.setLayout(layout)

    def add_asset(self):

        self.name = self.name_field.text()
        item = self.speSelectionW.currentItem()
        self.path_spe = self.SPECIALITY[item.text()]
        destination_folder = os.path.join(self.path_spe+'/'+ self.name)

        if destination_folder:
            if os.path.exists(self.path_directory_copy):
                # Copy the source folder into the destination folder with the new name
                shutil.copytree(self.path_directory_copy, destination_folder)
                print(f"Le dossier a été copié et renommé avec succès en : {destination_folder}")
                self.on_change_callback()
                self.close()
            else:
                print("Le dossier source n'existe pas.")
        else:
            print("Le dossier existe déjà.")

    def openFileDialog(self):
        # Ouvrir le dialogue pour sélectionner un fichier d'image
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        # Filtre pour les types de fichiers
        file_filter = "Images (*.jpeg *.jpg *.png);;Tous les fichiers (*)"
        
        # Ouvrir le dialogue
        file_name, _ = QFileDialog.getOpenFileName(self, "Sélectionnez une image", "", file_filter, options=options)

        if file_name:
            pixmap = QPixmap(file_name)             # Charger l'image et la redimensionner
            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)# Redimensionner l'image à 64x64

            if pixmap.width() > 64 and pixmap.height() > 64:                # Rognage pour obtenir une image de 64x64
                x = (pixmap.width() - 64) // 2                  # Calculer le centre pour le rognage
                y = (pixmap.height() - 64) // 2
                cropped_pixmap = pixmap.copy(x, y, 64, 64)
            else:
                cropped_pixmap = pixmap                     # Si l'image est plus petite, on l'affiche telle quelle

            self.imageLabel.setPixmap(cropped_pixmap)       # Afficher l'image rognée dans le QLabel
            self.image_path = file_name

class RemoveDirectoryWindow(QWidget):
    def __init__(self, directory, on_change_callback):
        super().__init__()
        self.directory = directory
        self.on_change_callback=on_change_callback

        self.setWindowTitle("Sous-fenêtre - Remove Directory")
        self.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout()
        layout_button = QHBoxLayout()
        label = label_cstm.labelCustom(f'warning: are you sure you want to delete the directory\n{self.directory}')
        label.body_text()
        cancel_button = QPushButton('CANCEL')
        cancel_button.clicked.connect(self.close)
        apply_button = QPushButton('APPLY')
        apply_button.clicked.connect(self.delete_directory)
        layout_button.addWidget(cancel_button)
        layout_button.addWidget(apply_button)
        
        layout.addWidget(label)
        layout.addLayout(layout_button)
        self.setLayout(layout)

    def delete_directory(self):
        if os.path.exists(self.directory):
            try:

                # Envoyer le répertoire à la corbeille
                shutil.rmtree(self.directory)
                print(f"Le répertoire {self.directory} a été envoyé à la corbeille avec succès.")
            except Exception as e:
                print(f"Erreur lors de l'envoi du répertoire à la corbeille : {e}")
        self.on_change_callback()
        self.close() 

class ManageDirectoryWidget(QWidget):
    def __init__(self, removeWindow, addWindow, directory=None, directory_delete=None, directory_copy=None, on_change_callback=None, parent=None):
        super(ManageDirectoryWidget, self).__init__(parent)
        self.removeWindow = removeWindow
        self.addWindow = addWindow
        self.directory = directory
        self.directory_delete=directory_delete
        self.directory_copy=directory_copy
        self.on_change_callback=on_change_callback
        
        self.init_ui()

    def init_ui(self):
        self.manageWidget = QWidget()

        def createButton(text=None):
            button = QPushButton(text)
            button.setFixedSize(32, 32)
            return button

        self.addButton = createButton('➕')
        self.removeButton = createButton('➖')

        self.addButton.clicked.connect(self.open_add_window)
        self.removeButton.clicked.connect(self.open_remove_window)

        assetManageLayout = QHBoxLayout(self.manageWidget)
        assetManageLayout.setAlignment(Qt.AlignLeft)
        assetManageLayout.addWidget(self.addButton)
        assetManageLayout.addWidget(self.removeButton)

        # Apply layout to the main widget
        self.setLayout(assetManageLayout)

    def open_add_window(self):
        if self.directory:
           if os.path.isdir(self.directory):
                self.addDirectoryWindow = self.addWindow(directory=self.directory, directory_copy=self.directory_copy, on_change_callback=self.on_change_callback)
                self.addDirectoryWindow.show()

    def open_remove_window(self):
        if isinstance(self.directory_delete, QListWidget):
        # Obtenez l'élément actuellement sélectionné
            current_item = self.directory_delete.currentItem()
            item = current_item.data(Qt.UserRole)
            path = item['full_path']
            if path:
                if os.path.isdir(path):
                    self.removeDirectoryWindow = self.removeWindow(directory=path, on_change_callback=self.on_change_callback)
                    self.removeDirectoryWindow.show()
