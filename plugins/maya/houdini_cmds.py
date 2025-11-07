import hou
import os
import shutil

class OpenInHoudini():
    def __init__(self):
        self.soft = 'houdini'
        self.format = '.hip'
    def get_scene (self):
        SCENE={}
        path_houdini_file = hou.hipFile.name()
        if path_houdini_file:
            SCENE['path_file'] = path_houdini_file
            SCENE['directory'] = os.path.dirname(path_houdini_file)
            SCENE['name'] = os.path.splitext(os.path.basename(path_houdini_file))[0]
            SCENE['type'] = os.path.splitext(path_houdini_file)[1]
            return SCENE
        else:
            print("Aucun fichier Maya ouvert")

    def save_as_scene(self, scene_name, new_scene_name, directory):
        try:
            # Créer le chemin complet pour la nouvelle scène
            new_scene_path = f"{directory}/{new_scene_name}.hipnc"  # Assurez-vous que l'extension est appropriée

            # Charger la scène actuelle
            current_scene = hou.hipFile.name()

            if current_scene != scene_name:
                return f"Erreur : La scène actuelle ({current_scene}) ne correspond pas à {scene_name}."

            # Sauvegarder la scène sous un nouveau nom
            hou.hipFile.save(new_scene_path)
            return f"Sauvegarde réussie : {new_scene_path}"

        except Exception as e:
            return f"Erreur lors de la sauvegarde de la scène : {str(e)}"

    def publish_scene(self, filename):
        hou.hipFile.save()
        file = self.get_scene()
        shutil.copy(file['path_file'], filename+'.hipnc')