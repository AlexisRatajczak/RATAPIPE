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
import computer_data
from importlib import reload
reload(set_data)
reload(cmn_file_cmds)
reload(computer_data)



class User:
    def __init__(self):
        self.hostname = computer_data.get_hostname()
        self.json_file = set_data.JsonHandler("config/pipeline_data.json")
        #if self.user in self.json_file.read_json():

    def update_data(self, name:str= "", spe = ""):
        self.data = {'name': name,
            'spe' : spe
            }
        self.json_file.update_item(self.hostname, self.data)

    def get_data(self):
        data = self.json_file.read_json()
        if self.hostname in data:
            return data[self.hostname]

    def set_name(self, name):
        data = self.json_file.read_json()
        if self.hostname in data:
            self.json_file.update_item(f"{self.hostname}.name", name)

    def remove_spe(self, value):
        data = self.json_file.read_json()
        if self.hostname in data:
            if value in data[self.hostname]['spe']:
                self.json_file.remove_value(f"{self.hostname}.spe", value)

    def add_spe(self,value, add=True):
        data = self.json_file.read_json()
        if self.hostname in data:
            print(self.hostname+"['spe']")
            self.json_file.update_item(f"{self.hostname}.spe", value, add = add)


user=User()



