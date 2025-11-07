import os
import shutil
import re
import unicodedata
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide2.QtCore import Qt

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

class SequenceExplorer():
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.full_path = None
        self._folderSelected = ""  # Variable privée pour le chemin du dossier sélectionné
        self.fileSelected = ""
        self.level = None
        self.init_ui()

    def init_ui(self):
        # Créer les onglets
        self.tabAsset = QWidget()

        # Dictionnaire pour les spécialités
        self.SPECIALITY ={
            'sequence' : {
                'Layout': {'nomenclature': 'layout',
                            'path': '/_houdini/hip/layout_TLO'},
                'Lighting': {'nomenclature': 'lighting',
                                'path': '/_houdini/hip/lighting'},
                'USD': {'nomenclature': 'usd',
                                'path': '/_usd'}},
            'shot' : {
                'Layout': {'nomenclature': 'layout',
                            'path': '/houdini/hip/layout'},
                'Lighting': {'nomenclature': 'lighting',
                                'path': '/houdini/hip/lighting'},
                'Animation': {'nomenclature': 'anim',
                            'path': '/maya/scenes/anim'},
                'Fx': {'nomenclature': 'fx',
                            'path': '/houdini/hip/fx'},
                'Compositing': {'nomenclature': 'compositing',
                            'path': '/nuke'},
                'Camera': {'nomenclature': 'camera',
                            'path': '/camera'},
                'USD': {'nomenclature': 'usd',
                                'path': '/usd'}}   
            }
    

        self.NavW = sceneNav_cstm.NavWidget(self.root_path, on_change_callback=self.update_full_path_spe, scene_widget_parent = True, scene_widget = True)
        self.manageAssetW = manageDirectory_cstm.ManageDirectoryWidget(removeWindow=manageDirectory_cstm.RemoveDirectoryWindow, addWindow=manageDirectory_cstm.AddDirectoryWindow, directory=self.root_path,  directory_delete=self.NavW.list_widget,
                                                   directory_copy="_template_shot", on_change_callback=self.reload_NavW)
        self.speSelectionW = list_cstm.listWidget(None, minWidth=140, maxWidth=260, fixeHeight = 120, on_change_callback=self.update_full_path)
        self.ScenesTableW = sceneTable_cstm.ScenesTableWidget(self.root_path, on_change_callback=self.reload_file )
        self.InfoDirectoryW = InfoDirectoryWidget(file=self.fileSelected, parent_directory='05_shot', spe_dict=self.SPECIALITY, advanced_dict=self.SPECIALITY, on_change_callback=self.reload_ScenesTableW)  


        self.speLabel = label_cstm.labelCustom("Select the speciality :")
        self.speLabel.subheading()

        self.shotListLayout = QVBoxLayout()
        self.shotListLayout.addWidget(self.NavW)
        self.shotListLayout.addWidget(self.manageAssetW)

        self.attributesLayout = QVBoxLayout()
        self.attributesLayout.setAlignment(Qt.AlignLeft)
        self.attributesLayout.addWidget(self.speLabel)
        self.attributesLayout.addWidget(self.speSelectionW)

        self.topLayout = QHBoxLayout()
        self.topLayout.setAlignment(Qt.AlignLeft)
        self.topLayout.addLayout(self.attributesLayout)

        self.scenesLayout = QVBoxLayout()
        self.scenesLayout.setAlignment(Qt.AlignLeft)
        self.scenesLayout.addLayout(self.topLayout, stretch= 1)
        self.scenesLayout.addWidget(self.ScenesTableW, stretch= 3)
        self.scenesLayout.addWidget(self.InfoDirectoryW, stretch= 1)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignLeft)
        self.mainLayout.addLayout(self.shotListLayout, stretch= 1)
        self.mainLayout.addLayout(self.scenesLayout, stretch= 3)
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
        self.update_full_path(spe = True)

    def update_full_path(self, spe = False):
        """Mise à jour du chemin complet avec les sélections 'publish' et 'spe'."""
        #try:
        itemSelected = self.NavW.itemSelected
        if itemSelected:  # Assurez-vous qu'un dossier est sélectionné
            data_item = itemSelected.data(Qt.UserRole)
            itemPath = data_item['full_path']

            itemLevel = data_item['level']
            
            if itemLevel == 0 :
                item_key = 'sequence'
            elif itemLevel == 1 :
                item_key = 'shot'

            if self.level != itemLevel:
                if spe:
                    self.speSelectionW.dict = self.SPECIALITY[item_key]
                    self.speSelectionW.clear()
                    print(111111111111111111)
                    self.speSelectionW.update_list()

            if self.speSelectionW.currentItem():
                selected_spe_item = self.speSelectionW.currentItem().text()
                print(self.SPECIALITY[item_key])
                print(selected_spe_item)
                if selected_spe_item in self.SPECIALITY[item_key]:
                    path_spe = self.SPECIALITY[item_key][selected_spe_item]['path']
                    self.full_path = os.path.join(itemPath + path_spe)

            self.level = itemLevel
            print(3)
            if os.path.exists(self.full_path):
                print(self.full_path)
                path = os.path.normpath(self.full_path)
                self.ScenesTableW.full_path_label.setText(f"Path: {path}")
                self.ScenesTableW.root_path = path
                self.ScenesTableW.update_scenes_list(path)
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
        print(100000000000000000, self.file)
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
                        if 'nuke' and 'sq0010' in self.path:
                            shutil.copy(file.template_compositing_sq0010, file.file_path)   
                        if 'nuke' and 'sq0020' in self.path:
                            shutil.copy(file.template_compositing_sq0020, file.file_path)   
                        if 'nuke' and 'sq0030' in self.path:
                            shutil.copy(file.template_compositing_sq0030, file.file_path)   
                        if 'nuke' and 'sq0040' in self.path:
                            shutil.copy(file.template_compositing_sq0040, file.file_path)   
                        if 'nuke' and 'sq0050' in self.path:
                            shutil.copy(file.template_compositing_sq0050, file.file_path)   
                        if 'nuke' and 'sq0060' in self.path:
                            shutil.copy(file.template_compositing_sq0060, file.file_path)   
                        else:
                            shutil.copy(file.template, file.file_path)
                    self.on_change_callback()
                else:
                    print('tu ne peux pas créer dans un dossier publish')
