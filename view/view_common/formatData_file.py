import os
from pathlib import Path
from datetime import datetime

class FormatDataFile():
    def __init__(self, full_path):
        self.full_path = full_path
        return
    def format_size(self):
        try:
            size = os.path.getsize(self.full_path)
        # Si la taille est inférieure à 1 Ko, on affiche directement
            if size < 1024:
                return f"{size} B"
            # Si la taille est inférieure à 1 Mo, on affiche en Ko
            elif size < 1024 * 1024:
                return f"{size / 1024:.2f} KB"
            # Sinon, on affiche en Mo
            else:
                return f"{size / (1024 * 1024):.2f} MB"
        except Exception as e:
            print(f"Erreur lors de la lecture de la taille du fichier: {e}")
        

    def format_date(self):
        path_f = Path(self.full_path)

        #récupérer la date de modification du fichier
        timestamp = path_f.stat().st_mtime
        date = datetime.fromtimestamp(timestamp)                # Convertir le timestamp en un objet datetime
        date_f = date.strftime('%d/%m/%Y %H:%M')
        return date_f