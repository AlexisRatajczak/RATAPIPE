import os
import unicodedata
import re

def rename_file(file_path, new_name):
    name_wo_accent = ''.join(
        c for c in unicodedata.normalize('NFD', new_name)
        if unicodedata.category(c) != 'Mn'
        )

    # Remplacer les caractères non alphanumériques (y compris les espaces) par "_"
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name_wo_accent)

    # Supprimer les underscores redondants (multiples underscores)
    final_name = re.sub(r'_+', '_', clean_name)


    # Sépare le nom de fichier de son extension
    path, name_file = os.path.split(file_path)
    print(name_file)
    name, extension = os.path.splitext(name_file)
    
    # Crée le nouveau nom en gardant l'extension originale
    new_file = f"{final_name}{extension}"
    new_path = os.path.join(path, new_file)
    
    # Renomme le fichier
    os.rename(file_path, new_path)
    
    print(f"Fichier renommé en : {new_path}")

