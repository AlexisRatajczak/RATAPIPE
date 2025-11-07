import sys
import os
import stat
import json
from importlib import reload

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


qt_platforms_path = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'PySide2', 'plugins', 'platforms')

module = ('view', 'ressources', 'plugins', 'data', 'config', 'common' )

for pck in module:
    if str(pck) not in sys.path:
        sys.path.append(str(pck)) 

from view import main_window  

reload(main_window)

def set_permissions_for_pipezer_folder():
    folder_path = os.path.expanduser('~/config')  # Ou l'emplacement spécifique de votre dossier .ratapipe
    try:
        # Forcer les droits de lecture et d'écriture pour l'utilisateur
        for root, dirs, files in os.walk(folder_path):
            os.chmod(root, stat.S_IRWXU)  # Répertoires
            for file in files:
                file_path = os.path.join(root, file)
                os.chmod(file_path, stat.S_IRWXU)  # Fichiers
        print(f"Les permissions pour {folder_path} ont été mises à jour.")
    except Exception as e:
        print(f"Erreur lors de la modification des permissions : {e}")

set_permissions_for_pipezer_folder()

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instanciation de votre MainWindow
        self.main_window = main_window.MainWindow()
        
        # Vous pouvez définir le titre et la taille de la fenêtre principale ici
        self.setWindowTitle("RATAPIPE")
        self.setGeometry(100, 100, 1250, 600)
        self.setMinimumWidth(1200)

        # Affichage du widget principal (MainWindow) dans la fenêtre
        self.setCentralWidget(self.main_window)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.show()  # Affiche la fenêtre principale
    sys.exit(app.exec_())  # Exécute l'application
