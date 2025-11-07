from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMenu, QAction, QInputDialog, QLineEdit, QMessageBox, QApplication, QListWidget, QTableWidget

import os
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
from plugins import file_cmds

class contextMenu():
    def __init__(self, parent=None, root_path =''):
        self.parent = parent
        self.root_path = root_path
        self.clipboard = QApplication.clipboard()
        self.menu = QMenu(self.parent)

    def show_context_menu(self, position):
        self.menu.exec_(self.parent.viewport().mapToGlobal(position))

    def add_action(self, name:str, action:callable):
        self.action = QAction(name, self.parent)
        self.action.triggered.connect(action)
        self.menu.addAction(self.action)

    def copy_path(self):
        if hasattr(self.parent, 'selectedItems'):
            selected_items = self.parent.selectedItems()  # Récupérer les éléments sélectionnés

            if selected_items:
                current_item = selected_items[0] 
                data_item = current_item.data(Qt.UserRole)
                self.clipboard.setText(data_item["full_path"])

    '''def paste_scene(self):
        if hasattr(self.parent, 'selectedItems'):
            selected_items = self.parent.selectedItems()  # Récupérer les éléments sélectionnés

            if selected_items:
                current_item = selected_items[0] 
                data_item = current_item.data(Qt.UserRole)
                self.clipboard.setText(data_item["full_path"])'''
    def open_in_explorer(self):
        print(self.parent)
        if hasattr(self.parent, 'selectedItems'):
            selected_items = self.parent.selectedItems()  # Récupérer les éléments sélectionnés
            if selected_items:
                print(selected_items)
                current_item = selected_items[0]
                data_item = current_item.data(Qt.UserRole)

                if "full_path" in data_item:
                    full_path = data_item["full_path"]
        
                    # Vérifier si le chemin existe
        if os.path.exists(full_path):
            # Ouvrir le chemin dans l'explorateur Windows
            subprocess.Popen(["explorer", "/select,", os.path.normpath(full_path)])
        else:
            QMessageBox.warning(self.parent, "Erreur", "Le chemin n'existe pas.")

    def rename_scene(self):
        # Vérifier si le widget parent a une méthode 'selectedItems'
        if hasattr(self.parent, 'selectedItems'):
            selected_items = self.parent.selectedItems()  # Récupérer les éléments sélectionnés

            if selected_items:
                current_item = selected_items[0]  # Sélectionner le premier élément
                data_item = current_item.data(Qt.UserRole)  # Récupérer les données via Qt.UserRole
                new_name, ok = QInputDialog.getText(self.parent, "Rename", "New name:", QLineEdit.Normal, data_item.get("name", ""))

                if ok and new_name:
                    # Mettre à jour le texte de l'élément sélectionné
                    current_item.setText(new_name)

                    # Vérifier si 'data_item' est un dictionnaire et a un chemin complet
                    if isinstance(data_item, dict) and "full_path" in data_item:
                        # Renommer le fichier via la fonction file_cmds.rename_file
                        file_cmds.rename_file(data_item["full_path"], new_name)

                        # Mettre à jour l'interface ou notifier l'utilisateur
                        QMessageBox.information(self.parent, "Information", f"Renommé en : {new_name}")
                    else:
                        QMessageBox.warning(self.parent, "Erreur", "Chemin complet non trouvé.")
            else:
                QMessageBox.warning(self.parent, "Attention", "Aucun élément sélectionné pour renommer.")
        else:
            QMessageBox.warning(self.parent, "Erreur", "Le widget ne supporte pas la sélection d'items.")