from datetime import datetime
from os import path

SESSION['APP'] = "Jeu Morpion"
SESSION['BASELINE'] = "Ismail AND Ndack"
SESSION['CURRENT_YEAR'] = datetime.now().year
SESSION['DIR_HISTORIQUE'] = path.join(SESSION['DIRECTORY'], "historiques")
SESSION['HISTORIQUE'] = dict()