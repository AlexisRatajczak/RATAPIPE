import socket
import sys
from pathlib import Path

# Chemin vers le répertoire contenant vos scripts
project_root = Path(__file__).resolve().parents[1] 
view_directory = project_root / "view"
common_directory = project_root / "common"

# Ajouter le chemin au sys.path
for directory in (view_directory, common_directory):
    if str(directory) not in sys.path:
        sys.path.append(str(directory)) 

import set_data
import common.cmn_file_cmds as cmn_file_cmds
from importlib import reload
reload(set_data)
reload(cmn_file_cmds)



def get_local_ip():
    # Récupérer l'adresse IP locale
    hostname = socket.gethostname()  # Récupérer le nom d'hôte
    local_ip = socket.gethostbyname(hostname)  # Récupérer l'adresse IP
    return local_ip

def get_hostname():
    hostname = socket.gethostname()
    return hostname