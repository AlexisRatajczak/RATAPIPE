from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from view.widgets_custom import label_cstm, checkboxStar_cstm, contextMenu_cstm
from common import set_data, user_cmds

class SceneWidget(QWidget):
    favToggle = Signal(str, bool)
    def __init__(self, scene_name):
        super().__init__()
        self.scene_name=scene_name
        # Crée les labels
        self.scene_name_label = label_cstm.labelCustom(scene_name)
        self.scene_name_label.listFormat()
        self.scene_name_label.setMaximumWidth(300)
        self.scene_name_label.setStyleSheet("background-color: transparent;")

        self.favbutton = checkboxStar_cstm.starCheckBox()
        self.favbutton.stateChanged.connect(self.on_state_change)  # Connecte le signal au slot

        # Layout principal
        mainLayout = QHBoxLayout()
        mainLayout.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.favbutton)
        mainLayout.addWidget(self.scene_name_label)
        self.setLayout(mainLayout)

    def on_state_change(self, state):
        if state == Qt.Checked: 
            self.favToggle.emit(self.scene_name, True)
            print("check")
        else:
            self.favToggle.emit(self.scene_name, False)
            print("uncheck")

    def setIndentation(self, level):
        # Ajouter de la marge gauche selon le niveau d'indentation
        indent_size = level * 30  # Par exemple, 20 pixels par niveau d'indentation
        self.layout().setContentsMargins(indent_size, 0, 0, 0)

class NavWidget(QWidget):
    def __init__(self, root_path, on_change_callback=None, scene_widget_parent = None, scene_widget=None, favori=None, parent=None):
        super(NavWidget, self).__init__(parent)
        self.root_path = root_path  # Chemin de départ
        self.on_change_callback = on_change_callback
        self.scene_widget_parent = scene_widget_parent
        self.scene_widget = scene_widget
        self.user = user_cmds.user
        self.favori = favori
        self.selected_folder_path = ""  # Stocker le chemin du dossier sélectionné
        self.itemSelected = ""
        self.fav_file = set_data.JsonHandler("config/pipeline_data.json")
        self.init_ui()

    def init_ui(self):
        self.navWidget = QWidget()

        # Ajout du champ de recherche
        self.search_box = QLineEdit()
        self.search_box.setMinimumWidth(140)  # Taille minimale
        self.search_box.setMaximumWidth(230)
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self.filter_list)  # Correction ici

        self.favbutton = checkboxStar_cstm.starCheckBox()
        self.favbutton.stateChanged.connect(self.filter_fav)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(140)  # Taille minimale
        self.list_widget.setMaximumWidth(260)
        self.populate_folders(self.root_path)  # Lister les dossiers et fichiers du répertoire initial
        self.list_widget.itemDoubleClicked.connect(self.on_item_doubleClicked)  # Connecter le clic sur un élément de la liste à une fonction de gestion
        self.list_widget.itemClicked.connect(self.on_item_clicked)

        self.filterLayout = QHBoxLayout()
        self.filterLayout.addWidget(self.search_box)
        self.filterLayout.addWidget(self.favbutton)

        self.mainLayout = QVBoxLayout(self.navWidget)
        self.mainLayout.addLayout(self.filterLayout)
        self.mainLayout.addWidget(self.list_widget)  # Ajouter la liste au layout

        self.setLayout(self.mainLayout)

        self.contextMenu = contextMenu_cstm.contextMenu(self.list_widget, self.root_path)
        self.contextMenu.add_action("Open in File Explorer", self.contextMenu.open_in_explorer)

        # Configurer le menu contextuel
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.contextMenu.show_context_menu)

    def set_fav(self, item, state):
        if state == True: 
            print("check")
            print(item)
            '''json = self.fav_file.read_json()
            if json["asset_fav"]:
                if json["asset_fav"] == item:
                    list_fav = list(json["asset_fav"])
                    list_fav.append(item)
                    self.fav_file.update_item("asset_fav", item)
            else:'''
            self.fav_file.update_item(f"{self.user.hostname}.{self.favori}", item, add=True)

        else:
            self.fav_file.remove_value(f"{self.user.hostname}.{self.favori}", item)
            print("uncheck")

    def filter_fav(self, state):
        if state == Qt.Checked: 
            print("check")

            data = self.fav_file.read_json()

            self.list_widget.clear()
            self.populate_folders(self.root_path)
            for index in range(self.list_widget.count()- 1, -1, -1):
                item = self.list_widget.item(index)
                self.on_item_clicked(item)

            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)  # Récupérer l'élément à l'index donné
                data_item = item.data(Qt.UserRole)
                if data_item['name'] not in data[self.user.hostname][self.favori]:
                    item.setHidden(True)
        else:
            self.list_widget.clear()
            self.populate_folders(self.root_path) 


            print("uncheck")

    def filter_list(self):
        """Filtre les éléments dans la QListWidget en fonction du texte de recherche."""
        search_text = self.search_box.text().lower()
        self.list_widget.clear()
        self.populate_folders(self.root_path) 
        
        if search_text != '':
            # Parcourir chaque élément de la liste après avoir peuplé les dossiers
            for index in range(self.list_widget.count()- 1, -1, -1):
                item = self.list_widget.item(index)
                self.on_item_clicked(item)
        
            # Parcourir tous les éléments et appliquer le filtre
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)  # Récupérer l'élément à l'index donné
                data_item = item.data(Qt.UserRole)
                if search_text in data_item['name'].lower():  # Comparer le texte de l'élément avec le texte de recherche
                    item.setHidden(False)  # Afficher l'élément s'il correspond
                else:
                    item.setHidden(True)  # Masquer l'élément s'il ne correspond pas
        else:
            print('None')

    def populate_folders(self, path, parent_item=None):
        """Cette fonction remplit la QListWidget avec les dossiers et fichiers du chemin spécifié."""
        self.list_widget.clear()
        try:
            # Liste les dossiers et fichiers uniquement dans le dossier racine
            for item_name in os.listdir(path):
                full_path = os.path.join(path, item_name)
                if os.path.isdir(full_path):  # Si c'est un dossier
                    if "_" not in item_name[0]:  # Ajouter uniquement les dossiers principaux dans QListWidget

                        if self.scene_widget_parent:
                            # Si SceneWidget est activé
                            scene_widget = SceneWidget(item_name)
                            json = self.fav_file.read_json()
                            if self.user.hostname in json and self.favori in json[self.user.hostname]:
                                if scene_widget.scene_name in json[self.user.hostname][self.favori]:
                                    scene_widget.favbutton.setChecked(True)
                            scene_widget.favToggle.connect(self.set_fav)

                            list_item = QListWidgetItem()
                            list_item.setSizeHint(scene_widget.sizeHint())  # Ajuster la taille
                            data = {"full_path": full_path, "name": item_name, "level": 0 ,}
                            list_item.setData(Qt.UserRole, data)  # Correctement utiliser setData ici
                            list_item.level = 0

                            # Insérer dans le QListWidget
                            self.list_widget.addItem (list_item)
                            self.list_widget.setItemWidget(list_item, scene_widget)

                        else:
                            folder_item = QListWidgetItem(item_name)
                            data = {"full_path": full_path, "name": item_name, "level": 0 ,}
                            folder_item.setData(Qt.UserRole, data)
                            folder_item.level = 0  # Niveau racine
                            self.list_widget.addItem(folder_item)

        except Exception as e:
            print(f"Erreur lors de la lecture du répertoire: {e}")

    def on_item_doubleClicked(self, item):
        """Cette fonction gère le clic sur un dossier."""
        data_item = item.data(Qt.UserRole)
        folder_path = data_item['full_path']  # Récupérer le chemin complet du dossier cliqué
        self.selected_folder_path = folder_path  # Mettre à jour le chemin du dossier sélectionné

        # Vérifier si c'est un dossier du premier niveau
        if item.level == 0:
            # Si l'élément cliqué a déjà des sous-dossiers, les supprimer (replier)
            if hasattr(item, 'expanded') and item.expanded:
                self.collapse_folder(item)
            else:
                # Ajouter les fichiers et sous-dossiers du dossier cliqué
                self.populate_subfolders_and_files(folder_path, parent_item=item, scene_widget = self.scene_widget)
                item.expanded = True
                self.itemSelected = item
                self.on_change_callback()

        if item.level == 1:
            print(f'asset : {item.text()}')
            # Mettre à jour le QLabel avec le nom du dossier sélectionné
            print(data_item['full_path'])
            self.itemSelected = item
            self.on_change_callback()
            #update_full_path()  # Appeler cette méthode pour mettre à jour le QLabel et le chemin complet

    def populate_subfolders_and_files(self, path, parent_item, scene_widget):
        """Ajoute les sous-dossiers et fichiers pour le dossier cliqué."""
        #try:
        row = self.list_widget.row(parent_item) + 1  # Insérer sous le parent
        for item_name in os.listdir(path):
            full_path = os.path.join(path, item_name)

            if not item_name[0] == '_':

                if scene_widget:
                    # Si SceneWidget est activé
                    scene_widget = SceneWidget(item_name)
                    json = self.fav_file.read_json()
                    if self.user.hostname in json and self.favori in json[self.user.hostname]:
                        if scene_widget.scene_name in json[self.user.hostname][self.favori]:
                            scene_widget.favbutton.setChecked(True)
                    scene_widget.favToggle.connect(self.set_fav)

                    list_item = QListWidgetItem()
                    list_item.setSizeHint(scene_widget.sizeHint())  # Ajuster la taille
                    data = {"full_path": full_path, "name": item_name, "level": 1 ,}
                    list_item.setData(Qt.UserRole, data)  # Correctement utiliser setData ici
                    list_item.level = parent_item.level + 1  # Mettre à jour le niveau pour l'indentation
                    scene_widget.setIndentation(list_item.level)  # Gérer l'indentation visuelle

                    # Insérer dans le QListWidget
                    self.list_widget.insertItem(row, list_item)
                    self.list_widget.setItemWidget(list_item, scene_widget)

                else:
                    # Sinon, insérer un QListWidgetItem simple avec texte
                    folder_item = QListWidgetItem("  " * (parent_item.level + 1) + item_name)
                    data = {"full_path": full_path, "name": item_name, "level": 1 ,}
                    folder_item.setData(Qt.UserRole, data)  # Correctement utiliser setData ici
                    folder_item.level = parent_item.level + 1  # Niveau pour l'indentation

                    # Insérer dans le QListWidget
                    self.list_widget.insertItem(row, folder_item)

                row += 1
        #except Exception as e:
        #    print(f"Erreur lors de la lecture du répertoire: {e}")

    def collapse_folder(self, parent_item):
        """Cette fonction replie (enlève) les sous-dossiers et fichiers du dossier cliqué."""
        row = self.list_widget.row(parent_item) + 1
        while row < self.list_widget.count():
            next_item = self.list_widget.item(row)
            if hasattr(next_item, 'level') and next_item.level > parent_item.level:
                self.list_widget.takeItem(row)  # Supprimer l'élément s'il est à un niveau supérieur
            else:
                break
        parent_item.expanded = False


    def on_item_clicked(self, item):
        data_item = item.data(Qt.UserRole)
        folder_path = data_item['full_path']  # Récupérer le chemin complet du dossier cliqué
        self.selected_folder_path = folder_path
        print(data_item['full_path'])

        self.itemSelected = item
        self.on_change_callback()