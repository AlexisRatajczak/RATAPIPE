import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets
from PySide2.QtWidgets import QFrame, QComboBox
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from plugins.maya import maya_cmds
from view.widgets_custom import list_cstm, textField_cstm, label_cstm

class UsdExporter(QtWidgets.QWidget):
    SPECIALITY = {
        'geo': {
            'nomenclature': '_geo',
            'anim': False,
            'scale': True,
            'invertNormal':False,
            'settings':("exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;filterTypes=nurbsCurve;exportColorSets=0;exportComponentTags=1;defaultMeshScheme=catmullClark;eulerFilter=0;convertMaterialsTo=[];exportInstances=1;exportVisibility=1;stripNamespaces=0;worldspace=0;")
        },
        'anim': {
            'nomenclature': '_anim',
            'anim': True,
            'scale': False,
            'invertNormal':True,
            'settings':("exportUVs=0;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;filterTypes=nurbsCurve;exportColorSets=0;exportComponentTags=1;defaultMeshScheme=catmullClark;eulerFilter=0;convertMaterialsTo=[];exportInstances=1;exportVisibility=1;stripNamespaces=0;worldspace=0;")
        }
    }

    def __init__(self):

        maya = maya_cmds.MayaCmds()
        maya_scene = maya.get_scene()

        path_asset_folder = maya_scene['directory']
        for _ in range(4):
            path_asset_folder = os.path.dirname(path_asset_folder)
        
        self.usd_folder = os.path.join(path_asset_folder+ "/usd/")
        self.asset_name =  os.path.basename(path_asset_folder)

        self.init_ui()

    def init_ui(self):
        super(UsdExporter, self).__init__()
        self.setWindowTitle("USD Exporter")
        
        # widgets
        self.labelName = label_cstm.labelCustom('Name:')
        self.labelName.heading()
        self.textfieldW = textField_cstm.textFieldCustom()

        self.labelPath = label_cstm.labelCustom('Path:')
        self.labelPath.body_text()
        self.textfieldPathW = textField_cstm.textFieldCustom()

        self.listW = list_cstm.listWidget(dict=self.SPECIALITY, on_change_callback=self.update_widgets)
        self.listW.setCurrentRow(0)
        self.exportScaleCheckbox = QtWidgets.QCheckBox("scale at 0.01")
        self.exportInvertNormalCheckbox = QtWidgets.QCheckBox("invert normal")
        self.exportAnimationCheckbox = QtWidgets.QCheckBox("export the animation")
        self.startFrameLabel = QtWidgets.QLabel("Start Frame:")
        self.startFrameSpinBox = QtWidgets.QSpinBox()
        self.startFrameSpinBox.setRange(1, 100000)
        self.startFrameSpinBox.setValue(1001)
        self.endFrameLabel = QtWidgets.QLabel("End Frame:")
        self.endFrameSpinBox = QtWidgets.QSpinBox()
        self.endFrameSpinBox.setRange(1, 100000)
        self.endFrameSpinBox.setValue(1100)

        self.formatComboBox = QComboBox()
        self.formatComboBox.setFixedWidth(80)
        self.formatComboBox.addItem("usda")
        self.formatComboBox.addItem("usdc") 
        self.formatComboBox.setCurrentText("usda")

        self.exportButton = QtWidgets.QPushButton("Export in USD")

        def separatorW():
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)  # Ligne horizontale
            separator.setFrameShadow(QFrame.Sunken)  # Ombre de la ligne
            return separator
        
        # Layout 
        layoutName = QtWidgets.QHBoxLayout()
        layoutName.addWidget(self.labelName)
        layoutName.addWidget(self.textfieldW)

        layoutPath = QtWidgets.QHBoxLayout()
        layoutPath.addWidget(self.labelPath)
        layoutPath.addWidget(self.textfieldPathW)

        layoutExport = QtWidgets.QHBoxLayout()
        layoutExport.addWidget(self.exportButton)
        layoutExport.addWidget(self.formatComboBox)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layoutName)
        layout.addLayout(layoutPath)
        layout.addWidget(separatorW())
        layout.addWidget(self.listW)
        layout.addWidget(separatorW())
        layout.addWidget(self.exportScaleCheckbox)
        layout.addWidget(self.exportInvertNormalCheckbox)
        layout.addWidget(separatorW())
        layout.addWidget(self.exportAnimationCheckbox)
        layout.addWidget(self.startFrameLabel)
        layout.addWidget(self.startFrameSpinBox)
        layout.addWidget(self.endFrameLabel)
        layout.addWidget(self.endFrameSpinBox)
        layout.addWidget(separatorW())
        layout.addLayout(layoutExport)
        
        self.setLayout(layout)
        
        self.exportAnimationCheckbox.stateChanged.connect(self.toggle_frame_options)
        self.exportButton.clicked.connect(self.export_to_usd)
        
        # Désactiver les champs de frames au départ
        self.toggle_frame_options()
        self.update_widgets()

    def update_widgets (self):
        spe = self.listW.currentItem().text()
        self.textfieldW.text_field.setText(self.asset_name + self.SPECIALITY[spe]['nomenclature'])
        self.textfieldPathW.text_field.setText(self.usd_folder)
        if self.SPECIALITY[spe]['anim'] == True:
            self.exportAnimationCheckbox.setChecked(True)
        else:
            self.exportAnimationCheckbox.setChecked(False)
            
        if self.SPECIALITY[spe]['scale'] == True:
            self.exportScaleCheckbox.setChecked(True)
        else:
            self.exportScaleCheckbox.setChecked(False)
            
        if self.SPECIALITY[spe]['invertNormal'] == True:
            self.exportInvertNormalCheckbox.setChecked(True)
        else:
            self.exportInvertNormalCheckbox.setChecked(False)
        self.toggle_frame_options()

    def toggle_frame_options(self):
        #Active ou désactive les champs start/end frame selon la case d'animation
        is_checked = self.exportAnimationCheckbox.isChecked()
        self.startFrameLabel.setEnabled(is_checked)
        self.startFrameSpinBox.setEnabled(is_checked)
        self.endFrameLabel.setEnabled(is_checked)
        self.endFrameSpinBox.setEnabled(is_checked)

    def define_path_usd(self):
        self.usd_path = os.path.join(self.textfieldPathW.text_field.text(), self.textfieldW.text_field.text())
        print(self.usd_path)
        
    def reverse_normals_on_all_meshes():
        all_meshes = cmds.ls(type="mesh", long=True)

        if not all_meshes:
            cmds.warning("Aucun mesh trouvé dans la scène.")
            return
        all_transforms = cmds.listRelatives(all_meshes, parent=True, fullPath=True) or []
        cmds.select(all_transforms)
        for transform in all_transforms:
            try:
                cmds.polyNormal(transform, normalMode=0)
                print(f"Normales inversées pour : {transform}")
            except Exception as e:
                print(f"Erreur pour {transform} : {e}")
                
    def export_to_usd(self):
        self.define_path_usd()

        spe = self.listW.currentItem().text()
        export_scale = self.exportScaleCheckbox.isChecked()
        invert_normal = self.exportInvertNormalCheckbox.isChecked()
        export_animation = self.exportAnimationCheckbox.isChecked()
        start_frame = self.startFrameSpinBox.value()
        end_frame = self.endFrameSpinBox.value()
        format = self.formatComboBox.currentText()
        
        if export_scale:
            cmds.setAttr('_GEO_.scaleX', 0.01)
            cmds.setAttr('_GEO_.scaleY', 0.01)
            cmds.setAttr('_GEO_.scaleZ', 0.01)
            
        if invert_normal:
            self.reverse_normals_on_all_meshes()
        
        # Configuration des options d'export USD
        usd_options = self.SPECIALITY[spe]['settings']

        usd_options += f"defaultUSDFormat={format};"

        if export_animation:
            usd_options += f"animation=1;startTime={start_frame};endTime={end_frame};"
        else:
            usd_options += "animation=0;"

        
        
        # Définir directement le chemin de sauvegarde sans boîte de dialogue
        usd_path = self.usd_path  # Utilisation directe de self.usd_path

        # Assurez-vous que le plugin est chargé avant l'export
        cmds.loadPlugin("mayaUsdPlugin", quiet=True)
        print(usd_options)
        # Commande d'export
        cmds.file(usd_path, force=True, options=usd_options, typ="USD Export", pr=True, es=True)

        # Message de confirmation
        QtWidgets.QMessageBox.information(self, "Succès", f"Exporté en USD : {usd_path}")
        
        if export_scale:
            cmds.setAttr('_GEO_.scaleX', 1)
            cmds.setAttr('_GEO_.scaleY', 1)
            cmds.setAttr('_GEO_.scaleZ', 1)

        if invert_normal:
            self.reverse_normals_on_all_meshes()