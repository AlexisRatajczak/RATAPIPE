import os
import shutil
import unicodedata
import re

from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PySide2.QtCore import Qt

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root)) 

from view.widgets_custom import list_cstm, sceneNav_cstm, sceneTable_cstm, textField_cstm, manageDirectory_cstm, label_cstm, pushButton_cstm
from plugins import open_scene, software_class
from common import set_data


class AssetExplorer(QWidget):
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.full_path = None
        self._folderSelected = ""  # Variable privée pour le chemin du dossier sélectionné
        self.fileSelected = ""

        self.ADVANCED = {
            'Edit': {
                'nomenclature': 'v0001',
                'path': 'edit'
            },
            'Publish': {
                'nomenclature': 'pub',
                'path': 'publish'
            }
        }

        self.RESSOURCE = {
            'Preprod': {
                'nomenclature': 'preprod',
                'path': r'\preprod' 
            },
            'Review': {
                'nomenclature': 'review',
                'path': r'\review' 
            },
            'Textures': {
                'nomenclature': 'texture',
                'path': r'\textures' 
            },
            'Obj': {
                'nomenclature': 'obj',
                'path': r'\obj' 
            },
            'USD': {
                'nomenclature': 'usd',
                'path': r'\usd' 
            }
        }

        self.adv = self.ADVANCED['Edit']
        self.subspe = ''

        self.SPECIALITY = {
            'Modeling': {
                'nomenclature': 'modeling',
                'path': r'{subspe}\{adv}\modeling',
                'subspe': {
                    'maya': r'\maya\scenes',
                    'houdini': r'\houdini\hip'}
            },
            'Sculpting': {
                'nomenclature': 'sculpt',
                'path': r'\sculpt'
            },
            'Rigging': {
                'nomenclature': 'rig',
                'path': r'\maya\scenes\{adv}\rig'
            },
            'Texturing': {
                'nomenclature': 'texturing',
                'path': r'\paint_3D\{subspe}',
                'subspe': {
                    'mari': r'mari',
                    'substance painter': r'substance_painter'
                }
            },
            'Lookdev': {
                'nomenclature': 'lookdev',
                'path': r'\houdini\hip\{adv}\lookdev'
            }
        }
    
        self.init_ui()

    def init_ui(self):
        # Créer les onglets
        self.tabAsset = QWidget()
        self.tabAsset.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialisation des widgets
        self.NavW = sceneNav_cstm.NavWidget(self.root_path, on_change_callback=self.reload_paths, scene_widget=True, favori="asset_fav")    
        self.NavW.setFixedWidth(230)
        self.manageAssetW = manageDirectory_cstm.ManageDirectoryWidget(removeWindow=manageDirectory_cstm.RemoveDirectoryWindow, addWindow=manageDirectory_cstm.AddDirectoryWindow, directory=self.root_path, directory_delete=self.NavW.list_widget,
                                                   directory_copy="_template_workspace_asset", on_change_callback=self.reload_NavW)
        
        self.headingScene = label_cstm.labelCustom('SCENE')
        self.headingScene.heading()
        self.speSelectionW = list_cstm.listWidget(self.SPECIALITY, minWidth=50, maxWidth=150, on_change_callback=self.update_full_path_spe)
        self.subSpeSelectionW = list_cstm.listWidget(None, minWidth=50, maxWidth=150, on_change_callback=self.update_full_path)
        self.advancedSelectionW = list_cstm.listWidget(self.ADVANCED, minWidth=140, maxWidth=260, on_change_callback=self.update_full_path)
        self.advancedSelectionW.setCurrentRow(0)
        self.ScenesTableW = sceneTable_cstm.ScenesTableWidget(self.root_path, on_change_callback=self.reload_file )
        self.InfoDirectoryW = InfoDirectoryWidget(file=self.fileSelected, parent_directory='04_asset', spe_dict=self.SPECIALITY, advanced_dict=self.ADVANCED, adv = self.adv, on_change_callback=self.reload_ScenesTableW)

        self.headingRessource = label_cstm.labelCustom('RESSOURCE')
        self.headingRessource.heading()
        self.infoSelectionW = list_cstm.listWidget(self.RESSOURCE, minWidth=140, maxWidth=260, on_change_callback=self.update_ressource_path)
        self.ressourcesTableW = sceneTable_cstm.ScenesTableWidget(self.root_path)#, on_change_callback=self.reload_file )

        self.speLabel = label_cstm.labelCustom("Speciality:")
        self.speLabel.subheading()

        self.advancedLabel = label_cstm.labelCustom("Advanced:")
        self.advancedLabel.subheading()

        self.assetsListLayout = QVBoxLayout()
        self.assetsListLayout.addWidget(self.NavW)
        self.assetsListLayout.addWidget(self.manageAssetW)

        self.speLayout = QHBoxLayout()
        self.speLayout.addWidget(self.speSelectionW)
        self.speLayout.addWidget(self.subSpeSelectionW)
        
        self.speLayout2 = QVBoxLayout()
        self.speLayout2.setAlignment(Qt.AlignLeft)
        self.speLayout2.addWidget(self.speLabel)
        self.speLayout2.addLayout(self.speLayout)
        self.speLayout2.addStretch()      

        self.advancedLayout = QVBoxLayout()
        self.advancedLayout.setAlignment(Qt.AlignLeft)
        self.advancedLayout.addWidget(self.advancedLabel)
        self.advancedLayout.addWidget(self.advancedSelectionW)  
        self.advancedLayout.addStretch()      

        self.selectionLayout = QHBoxLayout()
        self.selectionLayout.setAlignment(Qt.AlignLeft)
        self.selectionLayout.addLayout(self.speLayout2)
        self.selectionLayout.addLayout(self.advancedLayout)    

        self.attributesLayout = QVBoxLayout()
        self.attributesLayout.setAlignment(Qt.AlignLeft)
        self.attributesLayout.addWidget(self.headingScene)
        self.attributesLayout.addLayout(self.selectionLayout)

        self.topLayout = QHBoxLayout()
        self.topLayout.setAlignment(Qt.AlignLeft)
        self.topLayout.addLayout(self.attributesLayout)

        self.scenesLayout = QVBoxLayout()
        self.scenesLayout.setAlignment(Qt.AlignTop)
        self.scenesLayout.addLayout(self.topLayout, stretch= 1)
        self.scenesLayout.addWidget(self.ScenesTableW, stretch= 3)
        self.scenesLayout.addWidget(self.InfoDirectoryW, stretch= 1)

        self.assetInfoLayout = QVBoxLayout()
        self.assetInfoLayout.setAlignment(Qt.AlignLeft)
        self.assetInfoLayout.addWidget(self.headingRessource)
        self.assetInfoLayout.addWidget(self.infoSelectionW)
        self.assetInfoLayout.addWidget(self.ressourcesTableW)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignLeft)
        self.mainLayout.addLayout(self.assetsListLayout, stretch= 1)
        self.mainLayout.addLayout(self.scenesLayout, stretch= 3)
        self.mainLayout.addLayout(self.assetInfoLayout, stretch= 3)
        #self.mainLayout.addStretch()
        self.tabAsset.setLayout(self.mainLayout)


    def reload_NavW(self):
        self.NavW.populate_folders(self.root_path)

    def reload_ScenesTableW(self):
        self.ScenesTableW.update_scenes_list(self.full_path)
    
    def reload_file(self):
        self.InfoDirectoryW.file = os.path.join(self.full_path, self.ScenesTableW.file_path)

    def reload_paths(self):
        try:
            self.update_full_path()
        except Exception as e:
            print(f"Une erreur est survenue: {e}")
        try:
            self.update_ressource_path()
        except Exception as e:
            print(f"Une erreur est survenue: {e}")

    def update_full_path_spe(self):
        self.update_full_path(spe=True)

    def update_full_path(self, spe = False):
        """Mise à jour du chemin complet avec les sélections 'publish' et 'spe'."""
        #try:
        itemSelected = self.NavW.itemSelected
        if itemSelected:  # Assurez-vous qu'un dossier est sélectionné
            data_item = itemSelected.data(Qt.UserRole)
            itemPath = data_item['full_path']

            if self.speSelectionW.currentItem():
                selected_spe_item = self.speSelectionW.currentItem().text()

            if self.advancedSelectionW.currentItem():
                selected_publish_item = self.advancedSelectionW.currentItem().text()
                self.adv = self.ADVANCED[selected_publish_item]

            if spe :
                self.subSpeSelectionW.clear()
                if 'subspe' in self.SPECIALITY[selected_spe_item]:
                    self.subSpeSelectionW.dict = self.SPECIALITY[selected_spe_item]['subspe']
                    self.subspe = list(self.SPECIALITY[selected_spe_item]['subspe'].items())[0][1]
                else:
                    self.subSpeSelectionW.dict = None

                self.subSpeSelectionW.update_list()
                self.subSpeSelectionW.setCurrentRow(0)


            if self.subSpeSelectionW.currentItem():
                selected_subspe_item = self.subSpeSelectionW.currentItem().text()
                self.subspe = self.SPECIALITY[selected_spe_item]['subspe'][selected_subspe_item]

            path_spe = self.SPECIALITY[selected_spe_item]['path']
            self.full_path = os.path.join(itemPath + path_spe.format(adv=self.adv['path'], subspe = self.subspe))

            print(self.full_path)


            if os.path.exists(self.full_path):
                print(self.full_path)
                # Mettre à jour l'affichage du QLabel avec le chemin complet
                path = os.path.normpath(self.full_path)
                self.ScenesTableW.full_path_label.setText(f"Path: {path}")
                self.ScenesTableW.root_path = path
                self.ScenesTableW.update_scenes_list(path)
                self.InfoDirectoryW.path = path

                # Imprimer le chemin complet dans la console
                print(f"Chemin complet : {self.full_path}")
                return self.full_path
            else:
                return None
            
    def update_ressource_path(self):
        """Mise à jour du chemin complet avec les sélections 'publish' et 'spe'."""
        #try:
        itemSelected = self.NavW.itemSelected
        if itemSelected:  # Assurez-vous qu'un dossier est sélectionné
            data_item = itemSelected.data(Qt.UserRole)
            itemPath = data_item['full_path']
            selected_ressource_item = self.infoSelectionW.currentItem().text()

            # Construire le chemin complet avec les informations 'spe' et 'publish'
            self.ressource_path = os.path.join(itemPath + self.RESSOURCE[selected_ressource_item]['path'])

            if os.path.exists(self.ressource_path):
                print(self.ressource_path)
                # Mettre à jour l'affichage du QLabel avec le chemin complet
                path = os.path.normpath(self.ressource_path)
                self.ressourcesTableW.full_path_label.setText(f"Path: {path}")
                self.ressourcesTableW.root_path = path
                self.ressourcesTableW.update_scenes_list(path)

                # Imprimer le chemin complet dans la console
                print(f"Chemin complet : {self.ressource_path}")
                return self.ressource_path
            else:
                return None
        #except Exception as e:
        #    print(f"Erreur lors de la création du full_path: {e}")




class InfoDirectoryWidget (QWidget):
    def __init__(self, file=None, path=None, parent_directory=None, spe_dict=None, advanced_dict=None, adv=None,  on_change_callback=None, parent=None):
        super(InfoDirectoryWidget, self).__init__(parent)
        self.file = file
        self.path = path
        self.parent_directory = parent_directory
        self.spe_dict = spe_dict
        self.advanced_dict = advanced_dict
        self.adv = adv
        self.on_change_callback=on_change_callback

        softwaresData_path = "config/softwares_data.json"
        self.softwaresData = set_data.JsonHandler(softwaresData_path)
        self.software_info = self.softwaresData.read_json()


        self.init_ui()

    def init_ui(self):
        self.infoWidget = QWidget()


        self.label_commentaire = label_cstm.labelCustom('Enter the name of the new directory:')
        self.label_commentaire.body_text()
        self.open_button = pushButton_cstm.pushButtonCustom('open', size=(180,34))

        self.open_button.clicked.connect(self.open_file)


        self.new_scene_button = pushButton_cstm.pushButtonCustom('new_scene', size=(180,34))

        self.new_scene_button.clicked.connect(self.new_scene)

        self.name_text_field = textField_cstm.textFieldCustom()

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.open_button)  # Ajouter la liste au layout
        buttonLayout.addWidget(self.new_scene_button)      

        navLayout = QVBoxLayout(self.infoWidget)
        navLayout.addLayout(buttonLayout)  # Ajouter la liste au layout
        navLayout.addWidget(self.name_text_field)

        self.setLayout(navLayout)

    def open_file(self):
        print(self.file)
        file = software_class.SoftwareFileInfo(self.file)
        scene = open_scene.SoftwareOpener(file.file_path, file.executable, file.extension)
        scene.open_file()

    def new_scene(self):
        print(self.path)
        print('new_scene')
        if os.path.exists(self.path):
            path_parts = self.path.split(os.sep)

            if self.name_text_field.checkbox.isChecked() == False:
            # Trouver l'index du dossier 'self.parent_directory'
                if self.parent_directory in path_parts:
                    index = path_parts.index(self.parent_directory)
                    
                    # Le deuxième dossier suivant après 'self.parent_directory'
                    if index + 2 < len(path_parts):
                        subdirectory_name = os.path.normpath(path_parts[index + 2]).split(os.sep)[0]
                        print(subdirectory_name)
                    else:
                        print(f"Il n'y a pas de dossier après {self.parent_directory}.")
                        return
                else:
                    print(f"Le dossier {self.parent_directory} n'est pas dans le chemin.")
                    return
            else:
                chaine_sans_accent = ''.join(
                    c for c in unicodedata.normalize('NFD', self.name_text_field.text_field.text())
                    if unicodedata.category(c) != 'Mn'
                    )

                # Remplacer les caractères non alphanumériques (y compris les espaces) par "_"
                chaine_propre = re.sub(r'[^a-zA-Z0-9]', '_', chaine_sans_accent)

                # Supprimer les underscores redondants (multiples underscores)
                subdirectory_name = re.sub(r'_+', '_', chaine_propre)

            for key, value in self.advanced_dict.items():
                if self.advanced_dict[key]['path'] in self.path:
                    self.adv = self.advanced_dict[key]
                    break
            
            should_break = False
            for key, value in self.spe_dict.items():
                if 'subspe' in self.spe_dict[key]:
                    for subkey, subvalue in self.spe_dict[key]['subspe'].items():
                        self.subspe = subkey
                        spe_name = self.spe_dict[key]
                        path_formated = self.spe_dict[key]['path'].format(adv=self.adv['path'], subspe = self.spe_dict[key]['subspe'][self.subspe])
                        if path_formated in self.path:
                            should_break=True
                            break
                    if should_break:
                        break
                else:
                    spe_name = self.spe_dict[key]
                    path_formated = self.spe_dict[key]['path'].format(adv=self.adv['path'])
                    if path_formated in self.path:
                        break
           
                
            if subdirectory_name and spe_name:
                if not self.adv['nomenclature'] == 'pub':
                    name_file = subdirectory_name+'_'+spe_name['nomenclature']+'_'+self.adv['nomenclature']
                    for software, info in self.software_info.items():
                        if info["path_detect"] in self.path:
                            path_file = os.path.join(self.path+'/'+ name_file + info["default_extension"])
                            break
                        else:
                            path_file = None
                    if path_file == None:
                        return
                    
                    file = software_class.SoftwareFileInfo(path_file)
                    if not os.path.exists(file.file_path):
                        if 'lookdev' in self.path:
                            shutil.copy(file.template_lookdev, file.file_path)
                        elif 'modeling' in self.path:
                            print('modeling')
                            shutil.copy(file.template_modeling, file.file_path)
                        else:
                            print('maya')
                            shutil.copy(file.template, file.file_path)
                    self.on_change_callback()
                else:
                    print('tu ne peux pas créer dans un dossier publish')
