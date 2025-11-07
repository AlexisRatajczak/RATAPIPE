
import os
import subprocess
from pathlib import Path
import maya.cmds as cmds

class MayaCmds():
    def __init__(self):

        self.soft = 'maya'
        self.format = '.ma'
        self.template = r"\\storage\esma\3D4\sink\11_script\PIPEMANAGER\ressources\_template_maya.ma"
        self.executable = r'C:\Program Files\Autodesk\Maya2024\bin\maya.exe'
        

    def get_open_scene_name(self):
        current_scene = cmds.file(q=True, sn=True)
        return current_scene if current_scene else None
    
    def get_scene (self):
        SCENE={}
        path_maya_file = cmds.file(query=True, sceneName=True)
        if path_maya_file:
            SCENE['path_file'] = path_maya_file
            SCENE['directory'] = os.path.dirname(path_maya_file)
            SCENE['name'] = os.path.splitext(os.path.basename(path_maya_file))[0]
            SCENE['type'] = os.path.splitext(path_maya_file)[1]
            return SCENE
        else:
            print("Aucun fichier Maya ouvert")
        

    def get_selection (self):
        # Vérifie si une sélection est faite
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning("Aucune sélection à exporter.")
            return
        else:
            return selection

    def save_as_scene(self, scene_name, new_scene_name, directory):
        """
        Sauvegarde la scène actuelle de Maya avec un nom et un chemin spécifiés.
        
        :param scene_name: Nom du fichier de la scène (sans extension)
        :param directory: Répertoire où le fichier sera sauvegardé
        """
        if not os.path.exists(directory):  # Vérifie si le répertoire existe, sinon il le crée
            os.makedirs(directory)
        
        file_path = os.path.join(directory, new_scene_name + ".ma")  # Crée le chemin complet du fichier
        print(f"Tentative de sauvegarde de la scène : {new_scene_name} dans {directory}")
        print(file_path)  # Affiche le chemin du fichier
        
        try:
            current_file = scene_name  # Récupère le nom de la scène actuelle
            if current_file:
                # Renomme le fichier actif avec le nouveau chemin
                cmds.file(current_file, rename=file_path)
                # Sauvegarde le fichier
                cmds.file(save=True)  
                print(f"Scène sauvegardée avec succès : {file_path}")
            else:
                print("Aucune scène n'est ouverte. Impossible de sauvegarder.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la scène : {e}")


    def open_maya_file(self, file_path):
        # Chemin vers l'exécutable de Maya
        maya_executable = self.executable  # Modifiez si nécessaire

        # Normaliser le chemin du fichier pour éviter les conflits de séparateurs
        file_path = os.path.normpath(file_path)
        print(f"Tentative d'ouverture du fichier : {file_path}")

        # Vérification si le fichier est un .ma ou .mb
        if not file_path.endswith(('.ma', '.mb')):
            print("Le fichier sélectionné n'est pas un fichier Maya (.ma ou .mb).")
            return

        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            print(f"Le fichier {file_path} n'existe pas.")
            return

        # Vérifier si l'exécutable de Maya existe
        if os.path.exists(maya_executable):
            try:
                print("Lancement de Maya avec le fichier...")
                # Lancer Maya avec le fichier en argument en utilisant shell=True
                command = f'"{maya_executable}" -file "{file_path}"'
                subprocess.run(command, shell=True, check=True)
                print(f"Maya a été lancée avec succès avec le fichier {file_path}.")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors du lancement de Maya : {e}")
        else:
            print("L'exécutable de Maya n'a pas été trouvé.")


    def set_project(self, project_path):
        # Vérifiez si le chemin du projet existe
        if os.path.exists(project_path):
            # Définir le projet
            cmds.workspace(project_path, openWorkspace=True)
            print(f"Le projet a été défini sur : {project_path}")
        else:
            print("Le chemin du projet spécifié n'existe pas.")

    def publish_scene(self, filename):
        print('export', filename)
        selection = cmds.ls(sl = True)

        # Sélectionner tous ces objets dans la scène
        if selection:
            
            # Exporter la sélection dans un fichier .ma
            cmds.file(filename, exportSelected=True, type="mayaAscii")
            
            print(f"Exported to {filename}")
        else:
            print("Aucun objet trouvé pour l'export.")


    def export_selection_usd(self, file_path):
        """
        Exporte des objets sélectionnés de Maya au format USD.
        
        :param file_path: Chemin complet du fichier USD à créer.
        :param selected_objects: Liste d'objets à exporter. Si None, exporte tout.
        """
        selection = self.get_selection()

        # Vérifie si des objets sont sélectionnés
        if not selection:
            cmds.warning("Aucun objet sélectionné pour l'exportation.")
            return


        # Exportation des objets sélectionnés au format USD
        for obj in selection:
            # Vérifie si l'objet existe
            if cmds.objExists(obj):
                # Exporter l'objet au format USD
                try:
                    # Exporter la sélection dans un fichier .ma
                    cmds.file(file_path, exportSelected=True, force=True, type="USD Export")
                    
                    #cmds.mayaUSD.exportSelected(file_path, selection=selection)
                    print(f"Exportation réussie : {file_path}")
                except Exception as e:
                    print(f"Erreur lors de l'exportation de {obj}: {e}")
            else:
                print(f"L'objet {obj} n'existe pas.")

    def export_selec_usd(self, file_path, UVs=True, Materials=False, Colors=False):
        # Vérifie si une sélection est faite
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning("Aucune sélection à exporter.")
            return

        # Filtrer la sélection pour exclure les NURBS curves
        valid_selection = [obj for obj in selection if cmds.nodeType(obj) != "nurbsCurve"]

        if not valid_selection:
            cmds.warning("La sélection ne contient que des NURBS curves. Aucun export effectué.")
            return

        # Construction de la commande d'exportation
        export_options = (
            'exportUVs=1;'
            'exportSkels=none;'
            'exportSkin=none;'
            'exportBlendShapes=0;'
            'exportDisplayColor=0;'
            'filterTypes=nurbsCurve;'
            'exportColorSets=0;'
            'exportComponentTags=1;'
            'defaultMeshScheme=catmullClark;'
            'animation=0;'
            'eulerFilter=0;'
            'staticSingleSample=0;'
            'startTime=1;'
            'endTime=1;'
            'frameStride=1;'
            'frameSample=0.0;'
            'defaultUSDFormat=usdc;'
            'parentScope=;'
            'shadingMode=useRegistry;'
            'convertMaterialsTo=[UsdPreviewSurface];'
            'exportRelativeTextures=automatic;'
            'exportInstances=1;'
            'exportVisibility=1;'
            'mergeTransformAndShape=1;'
            'stripNamespaces=0;'
            'worldspace=0'
        )

        # Exécuter la commande d'exportation
        try:
            cmds.file(file_path, force=True, options=export_options, typ="USD Export", pr=True, es=True)
            cmds.inform("Exportation USD terminée.")
        except Exception as e:
            cmds.warning(f"Erreur lors de l'exportation : {e}")

