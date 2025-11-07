import os
import sys
from pathlib import Path
import shutil
#from send2trash import send2trash
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from importlib import reload

# Chemin vers le répertoire contenant vos scripts
project_root = Path(__file__).resolve().parents[1] 
# Ajouter le chemin au sys.path
if str(project_root) not in sys.path:
    sys.path.append(str(project_root)) 


def set_software(open_in):
    if open_in == "maya":
        print("maya")
        from plugins.maya import maya_cmds
        reload(maya_cmds)
        software = maya_cmds.MayaCmds()
    elif open_in == "houdini":
        print("houdini")
        from plugins.houdini import houdini_cmds
        reload(houdini_cmds)
        software = houdini_cmds.OpenInHoudini()
    
    return software

def save_edit(open_in):
    software = set_software(open_in)
    file = software.get_scene()
    suffixe = file['name'][-4:]
    try:
        version = int(suffixe)
        if isinstance(version, int):
            new_version = str(version + 1).zfill(4)
            new_name = file['name'][:-4] + new_version
            software.save_as_scene(file['path_file'], new_name, file['directory'])
    except Exception as e:
        print(f"Erreur le fichier a mal été renommé: {e}")

def publish_usd(open_in):
    software = set_software(open_in)
    print('usd')
    maya_file = software.get_scene()
    path = maya_file['path_file']
    index = path.find(software.soft)

    # Vérifier si 'maya' a été trouvé
    if index != -1:
        new_path = path[:index + len(software.soft)]
        usd_folder = new_path.replace(software.soft,'usd')
        print(usd_folder)

        if "modeling" in path:
            new_name = maya_file['name'][:-5] + "geometry"
            print(usd_folder)
            print(new_name)
            path_usd = os.path.join(usd_folder+'/'+new_name)
        else:
            return
    
    software.export_selection_usd(file_path = path_usd)

def publish (open_in):
    software = set_software(open_in)
    print('publish')
    file = software.get_scene()
    suffixe = file['name'][-4:]
    try:
        version = int(suffixe)
        if isinstance(version, int):
            new_version = 'pub'
            new_name = file['name'][:-5] + new_version
            new_directory = file['directory'].replace('edit', 'publish')
            new_file = os.path.join(new_directory, new_name + software.format)

            if os.path.exists(new_file):
                backup_directory = os.path.join(new_directory+"/_backup")
                files_in_directory = [f for f in os.listdir(backup_directory) if os.path.isfile(os.path.join(backup_directory, f))]
                if not files_in_directory:
                    print("Le répertoire ne contient aucun fichier.")
                    new_value = str(1).zfill(4)
                else:
                    
                    largest_value = -1  # Initialiser à -1 pour s'assurer qu'on trouve des valeurs positives
                    # Parcourir tous les fichiers du répertoire
                    for filename in os.listdir(backup_directory):
                        file_path = os.path.join(backup_directory, filename)
                        if os.path.isfile(file_path):# Vérifier que c'est un fichier
                            name = os.path.splitext(os.path.basename(filename))[0]# Extraire les 4 derniers caractères du nom du fichier
                            suffix = name[-4:]
                            if suffix.isdigit():# Vérifier si le suffixe est composé uniquement de chiffres
                                value = int(suffix)
                                # Comparer la valeur avec la plus grande rencontrée jusqu'ici
                                if value > largest_value:
                                    largest_value = value
                                    new_value = str(largest_value + 1).zfill(4)
                
                new_backup_file = os.path.join(backup_directory+'/'+ new_name+'_v'+new_value + software.format)
                shutil.move(new_file, new_backup_file)
            new_file_path= (new_directory+'/'+new_name)
            software.publish_scene(new_file_path)
    except Exception as e:
        print(f"Erreur le fichier a mal été renommé: {e}")


def set_project(open_in):
    software = set_software(open_in)
    file = software.get_scene()
    path = file['path_file']
    index = path.find(software.soft)

    if index != -1:
        new_path = path[:index + len(software.soft)]
        software.set_project(new_path)
    else:
        print("le chemin d'accés ne comprende pas 'maya' dans son path pour pouvoir set project correctemnet")