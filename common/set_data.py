import sys
import os
import json
from pathlib import Path

class JsonHandler:
    def __init__(self, relative_path):
            # Sinon, utilisez le chemin normal du script
        base_path = Path(__file__).resolve().parents[1]  # Remonte de deux niveaux pour atteindre la racine

        # Construire le chemin complet vers le fichier JSON
        self.filename = base_path / relative_path

        data = self.read_json()
        if data == None:
            self.save_json({})

    def read_json(self):
        """Lit les données d'un fichier JSON et les renvoie sous forme de dictionnaire."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"Erreur : le fichier '{self.filename}' n'a pas été trouvé.")
            return None
        except json.JSONDecodeError:
            print(f"Erreur : le fichier '{self.filename}' n'est pas un JSON valide.")
            return None
        except Exception as e:
            print(f"Erreur inattendue lors de la lecture du fichier : {e}")
            return None

    def save_json(self, data):
        """Sauvegarde les données sous forme de dictionnaire dans un fichier JSON. 
        Crée le fichier si celui-ci n'existe pas."""
        try:
            # Crée le dossier s'il n'existe pas
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            # Sauvegarde les données dans le fichier
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Données sauvegardées dans '{self.filename}'.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")

    def create_json_file(self):
        """Crée un nouveau fichier JSON vide."""
        try:
            # Crée le dossier s'il n'existe pas
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            # Crée un fichier JSON vide
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump({}, file)
            print(f"Fichier '{self.filename}' créé.")
        except Exception as e:
            print(f"Erreur lors de la création du fichier : {e}")

    def update_item(self, key, value, add: bool = False):
        """
        Ajoute ou met à jour un élément dans le dictionnaire JSON.
        Peut gérer des clés imbriquées sous forme de chaîne (par exemple 'alexis.spe').
        """
        data = self.read_json()
        
        if data is not None:
            keys = key.split('.')  # Sépare la chaîne pour gérer les sous-clés
            d = data
            for k in keys[:-1]:
                d = d.setdefault(k, {})  # Accède ou crée un sous-dictionnaire si nécessaire
            
            last_key = keys[-1]  # La dernière clé à mettre à jour
            
            if last_key in d and add:
                if not isinstance(d[last_key], list):
                    d[last_key] = [d[last_key]]
                if value not in d[last_key]:  # Évite les doublons
                    d[last_key].append(value)
            else:
                d[last_key] = value  # Met à jour ou crée la clé avec la nouvelle valeur
            
            self.save_json(data)  # Sauvegarde les modifications
            print(f"Élément '{key}' a été mis à jour avec la valeur : {value}.")
            
    def remove_value(self, key, value):
        """
        Supprime une valeur spécifique dans une clé donnée (avec sous-clés possibles).
        """
        data = self.read_json()
        if data is not None:
            keys = key.split('.')  # Sépare la chaîne pour gérer les sous-clés
            d = data
            for k in keys[:-1]:
                d = d.get(k, {})  # Accède au sous-dictionnaire, ou retourne {} si la clé n'existe pas
            last_key = keys[-1]  # La dernière clé à laquelle on souhaite supprimer la valeur
            if last_key in d:
                if isinstance(d[last_key], list) and value in d[last_key]:
                    d[last_key].remove(value)  # Supprime la valeur de la liste
                    print(f"La valeur '{value}' a été supprimée de la clé '{key}'.")
                else:
                    print(f"La valeur '{value}' n'existe pas dans la clé '{key}'.")
            else:
                print(f"La clé '{key}' n'existe pas dans le fichier JSON.")
            
            # Écrire les modifications dans le fichier JSON
            self.save_json(data)  # Sauvegarde les modifications
        else:
            print("Impossible de lire les données JSON.")
