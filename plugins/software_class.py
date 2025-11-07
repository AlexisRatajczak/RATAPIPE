import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1] 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root)) 

from common import set_data

user = os.getenv("USER") or os.getenv("USERNAME")

class SoftwareFileInfo:
    # Dictionnaire contenant les informations sur les logiciels
    softwaresData_path = "config/softwares_data.json"
    softwaresData = set_data.JsonHandler(softwaresData_path)
    software_info = softwaresData.read_json()

    def __init__(self, file_path):
        self.file_path = file_path
        self.software_name = None
        self.executable = None
        self.file_type = None
        self.template = None  # Ajout d'un attribut pour le template
        self.template_lookdev = None
        self.template_modeling = None
        self.template_compositing_sq0010 = None
        self.template_compositing_sq0020 = None
        self.template_compositing_sq0030 = None
        self.template_compositing_sq0040 = None
        self.template_compositing_sq0050 = None
        self.template_compositing_sq0060 = None

        self.detect_software()

    def detect_software(self):
        # Vérifie l'extension du fichier pour déterminer le logiciel
        _, ext = os.path.splitext(self.file_path)
        for software, info in self.software_info.items():
            if ext.lower() in info['extensions']:
                self.software_name = software
                self.executable = info['executable']
                self.file_type = info['file_type']
                self.template = info['template']
                if 'template_lookdev' in info:
                    self.template_lookdev = info['template_lookdev']
                if 'template_modeling' in info:
                    self.template_modeling = info['template_modeling']
                if 'template_compositing_sq0010' in info:
                    self.template_modeling = info['template_compositing_sq0010']
                if 'template_compositing_sq0020' in info:
                    self.template_modeling = info['template_compositing_sq0020']
                if 'template_compositing_sq0030' in info:
                    self.template_modeling = info['template_compositing_sq0030']       
                if 'template_compositing_sq0040' in info:
                    self.template_modeling = info['template_compositing_sq0040']
                if 'template_compositing_sq0050' in info:
                    self.template_modeling = info['template_compositing_sq0050']
                if 'template_compositing_sq0060' in info:
                    self.template_modeling = info['template_compositing_sq0060']
                self.extension = ext.lower()
                return
        # Si aucun logiciel n'est trouvé
        self.software_name = 'Unknown'
        self.executable = None
        self.file_type = 'Unknown'
        self.template = None
        self.extension = 'Unknown'

    def __str__(self):
        return (f"File: {self.file_path}\n"
                f"Software: {self.software_name}\n"
                f"Executable: {self.executable}\n"
                f"File Type: {self.file_type}\n"
                f"Template: {self.template}")

