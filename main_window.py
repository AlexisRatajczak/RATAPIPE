import sys
import os
import re
from pathlib import Path
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QTabWidget, QSizePolicy, QPushButton, QTableWidget, QLabel, QListWidget, QLineEdit, QGraphicsDropShadowEffect
from PySide2.QtCore import Qt, Signal, Property, QTimer
from PySide2.QtGui import QColor



# Chemin vers le répertoire contenant vos scripts
project_root = Path(__file__).resolve().parents[1] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root)) 

# Importation des modules
from view import asset_viewer, sequence_viewer, taskbar
from common import set_data


class MainWindow(QWidget):
    # Signal pour le changement de path de la pipeline
    root_path_changed = Signal(str)

    # Signal pour la détection des changements dans le fichier colors.json
    color_data_changed = Signal()

    def __init__(self):
        super().__init__()

        # Initialisation de root_path
        pipeData_path = "config/pipeline_data.json"
        self.pipeData = set_data.JsonHandler(pipeData_path)
        self.dict_pipeData = self.pipeData.read_json()

        relative_path = "config/colors.json"
        self.colorData = set_data.JsonHandler(relative_path)

        if self.dict_pipeData:
            self._root_path = self.dict_pipeData['path']
            print('La pipeline sélectionnée est :', self._root_path)
        else:
            self._root_path = ''
            print("Aucune pipeline n'a été sélectionnée")
        
        self.init_ui()

        # Initialisation de last_color_data pour détecter les changements
        self.last_color_data = self.colorData.read_json()

        # Timer pour vérifier périodiquement les changements dans colors.json
        self.color_check_timer = QTimer(self)
        self.color_check_timer.timeout.connect(self.check_color_data_changes)
        self.color_check_timer.start(5000)  # Vérification toutes les 5 secondes

    def init_ui(self):
        # set tasksbar
        self.taskbar = taskbar.taskbar()
        self.taskbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.taskbar.pipeW.set_root_path(self._root_path)
        self.taskbar.pipeW.update_path_connect(self.set_root_path_from_line_edit)
        self.taskbar.pipePanel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.taskbar.userPanel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Créer un espace pour le contenu principal
        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.StyledPanel)
        self.taskbar.userPanel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.onglets = QTabWidget()
        self.update_widgets(self._root_path)

        self.layout_tab = QVBoxLayout(self.content_frame)
        self.layout_tab.setAlignment(Qt.AlignTop)
        self.layout_tab.addWidget(self.onglets)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.setSpacing(0)
        # add tasksbar to the mainLayout
        self.main_layout.addWidget(self.taskbar, stretch=3)
        self.main_layout.addWidget(self.taskbar.pipePanel, stretch=3)
        self.main_layout.addWidget(self.taskbar.userPanel, stretch=3)
        self.main_layout.addWidget(self.content_frame, stretch=1)

        # Créer un layout pour la partie contenu principal
        self.update_color_from_json()

        # Connexion du signal root_path_changed à la méthode de mise à jour des widgets
        self.root_path_changed.connect(self.update_widgets)

        # Connexion du signal color_data_changed à la méthode de mise à jour des couleurs
        self.color_data_changed.connect(self.update_color_from_json)

    def update_color_from_json(self):
        try:
            def updateSheet(item, key, settings):
                """Met à jour une propriété CSS d'un widget en conservant ses styles existants."""
                ss = item.styleSheet() or ""
                if key not in ss:
                    ss += f"{key}: {settings};"
                else:
                    # Remplacer uniquement la propriété spécifiée
                    ss = re.sub(
                        rf"{key}:\s*[^;]+;", 
                        f"{key}: {settings};", 
                        ss
                    )
                item.setStyleSheet(ss)

            def darken_color(hex_color, factor=0.2):
                # Convertir le hex en RGB
                hex_color = hex_color.lstrip('#')
                r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

                # Foncer chaque composant de la couleur (réduire les valeurs)
                r = int(r * (1 - factor))
                g = int(g * (1 - factor))
                b = int(b * (1 - factor))

                # Retourner la couleur en hexadécimal
                return f"#{r:02x}{g:02x}{b:02x}"

            dict_colorData = self.colorData.read_json()
            stylesheet = ""
            
            # Définir les styles globaux
            if 'color1' in dict_colorData:
                stylesheet += f"color: {dict_colorData['color1']};"
                for button in (self.findChildren(QPushButton) + self.findChildren(QLineEdit)):
                    updateSheet(button, 'border', f"1px solid {dict_colorData['color1']}")
            
            if 'color2' in dict_colorData:
                stylesheet += f"background-color: {dict_colorData['color2']};"

                darken_color2 = darken_color(dict_colorData['color2'])

                for widget in (self.findChildren(QTableWidget) + 
                    self.findChildren(QListWidget) + 
                    self.findChildren(QLineEdit)):

                    updateSheet(widget, 'background-color', f"{darken_color2}")
            
            # Appliquer la couleur de fond pour les sections spécifiques
            if 'color3' in dict_colorData:
                darken_color3 = darken_color(dict_colorData['color3'])

                self.taskbar.setStyleSheet(f"background-color: {dict_colorData['color3']};")
                self.taskbar.pipePanel.setStyleSheet(f"border: {dict_colorData['color3']};")
                self.taskbar.userPanel.setStyleSheet(f"border: {dict_colorData['color3']};")
                self.onglets.setStyleSheet(f"QTabBar::tab {{ background: {dict_colorData['color3']}; }} QTabBar::tab:selected {{ background: {darken_color3}; }}")

                #self.onglets.setStyleSheet(f"QTabBar::tab:selected {{ background: {darken_color3}; }}")

                # Appliquer la couleur, l'arrondi et l'ombre aux boutons, sauf ceux dans taskbar.userPanel
                for button in self.findChildren(QPushButton):
                    if button not in self.taskbar.userPanel.findChildren(QPushButton):
                        updateSheet(button, 'background-color', dict_colorData['color3'])
                        updateSheet(button, 'border-radius', '2px')  # Ajouter l'arrondi


                # Changer la couleur de fond de l'en-tête horizontal de QTableWidget
                for table in self.findChildren(QTableWidget):
                    table.horizontalHeader().setStyleSheet(
                        f"QHeaderView::section {{background-color: {dict_colorData['color3']};}}"
                    )
            
            # Appliquer le style global s'il existe
            if stylesheet:
                self.setStyleSheet(stylesheet)

        except Exception as e:
            print(f"Erreur lors de la mise à jour de la couleur: {e}")


                            

            '''if 'color4' in dict_colorData: 
                for widget in widgets_border:
                    updateSheet(widget, 'border', f"1px solid {dict_colorData['color4']}")'''


    def check_color_data_changes(self):
        """Vérifie si les données de couleur ont changé."""
        current_data = self.colorData.read_json()
        if current_data != self.last_color_data:
            print("Changement détecté dans les données de couleur.")
            self.last_color_data = current_data
            self.color_data_changed.emit()  # Émettre le signal pour signaler un changement

    @Property(str)
    def root_path(self):
        return self._root_path

    @root_path.setter
    def root_path(self, value):
        if self._root_path != value:
            self._root_path = value
            print("Root path changed to:", value)
            self.root_path_changed.emit(value)

    def set_root_path_from_line_edit(self):
        new_path = self.taskbar.pipeW.path_pipe_field.text()
        if self._root_path != new_path:
            self.root_path = new_path

    def update_widgets(self, new_path):
        print(f'Updating widgets with root_path: {new_path}')
        asset_directory = os.path.join(new_path, "04_asset")
        sequence_directory = os.path.join(new_path, "05_shot")

        if hasattr(self, 'asset_viewer'):
            print('Updating asset viewer')
            self.asset_viewer.root_path = asset_directory
            self.asset_viewer.NavW.root_path = asset_directory
            self.asset_viewer.manageAssetW.directory = asset_directory
            self.asset_viewer.NavW.populate_folders(asset_directory)
        else:
            print('Creating new asset viewer')
            self.asset_viewer = asset_viewer.AssetExplorer(asset_directory)
            self.onglets.addTab(self.asset_viewer.tabAsset, "Asset")

        if hasattr(self, 'sequence_viewer'):
            print('Updating sequence viewer')
            self.sequence_viewer.root_path = sequence_directory
            self.sequence_viewer.NavW.root_path = sequence_directory
            self.sequence_viewer.NavW.populate_folders(sequence_directory)
        else:
            print('Creating new sequence viewer')
            self.sequence_viewer = sequence_viewer.SequenceExplorer(sequence_directory)
            self.onglets.addTab(self.sequence_viewer.tabAsset, "Sequence")
            
        self.update_color_from_json()

    def resizeEvent(self, event):
        print(self.size())
        super().resizeEvent(event)
