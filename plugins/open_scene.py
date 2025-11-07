import os
import subprocess
import sys
from pathlib import Path

# Configuration de l'environnement pour inclure les plugins Qt
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

class SoftwareOpener:
    def __init__(self, file_path, executable, file_formats):
        self.file_path = file_path
        self.executable = executable  # Chemin vers l'exécutable du logiciel
        self.file_formats = file_formats  # Liste des formats de fichiers acceptés

    def configure_qt_plugins(self):
        """
        Configure les variables d'environnement nécessaires pour Qt et Maya.
        """
        # Définir la variable QT_PLUGIN_PATH pour inclure les plugins Qt de Maya
        qt_plugin_path = Path(self.executable).parent / "qt-plugins"
        os.environ["QT_PLUGIN_PATH"] = str(qt_plugin_path)

        # Vérification pour s'assurer que le chemin des plugins existe
        if not qt_plugin_path.exists():
            print(f"Attention : Le chemin QT_PLUGIN_PATH '{qt_plugin_path}' n'existe pas.")
        else:
            print(f"QT_PLUGIN_PATH configuré sur : {qt_plugin_path}")

        # Supprimer les conflits possibles avec d'autres installations Qt
        os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
        print("QT_QPA_PLATFORM_PLUGIN_PATH supprimé pour éviter les conflits.")

    def open_file(self):
        # Normaliser le chemin du fichier pour éviter les conflits de séparateurs
        self.file_path = os.path.normpath(self.file_path)
        print(f"Tentative d'ouverture du fichier : {self.file_path}")

        # Vérification si le fichier a un format valide
        if not any(self.file_path.endswith(fmt) for fmt in self.file_formats):
            print(f"Le fichier sélectionné n'est pas un fichier valide ({', '.join(self.file_formats)}).")
            return

        # Vérifier si le fichier existe
        if not os.path.exists(self.file_path):
            print(f"Le fichier {self.file_path} n'existe pas.")
            return

        # Vérifier si l'exécutable existe
        if os.path.exists(self.executable):
            print("Configuration des plugins Qt...")
            self.configure_qt_plugins()

            print("Lancement du logiciel avec le fichier...")
            # Lancer le logiciel avec le fichier en argument
            command = [self.executable, self.file_path]
            subprocess.Popen(command)
            print(f"Le logiciel a été lancé avec succès avec le fichier {self.file_path}.")
        else:
            print("L'exécutable n'a pas été trouvé.")

# Exemple d'utilisation
# software_opener = SoftwareOpener("path/to/file.ext", "path/to/maya.exe", [".mb", ".ma"])
# software_opener.open_file()

# maya_opener = SoftwareOpener("path/to/maya/file.ma", "path/to/maya.exe", [".ma", ".mb"])
# maya_opener.open_file()

# houdini_opener = SoftwareOpener("path/to/houdini/file.hip", "path/to/houdini.exe", [".hip", ".hipnc"])
# houdini_opener.open_file()
