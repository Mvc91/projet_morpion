from model.morpion_model import get_equipes, suppression
from controleurs.includes import add_activity

add_activity(SESSION['HISTORIQUE'], "suppression d'une équipe")

# Charger les équipes pour affichage
REQUEST_VARS['equipes'] = get_equipes(SESSION['CONNEXION'])

# Lire le nom via GET ou POST (dict de listes)
nom = POST.get('nom', [''])[0].strip() 

if nom:
    # Construire l'ensemble des noms existants
    noms_equipes = {e[1] for e in REQUEST_VARS['equipes']}
    if nom not in noms_equipes:
        REQUEST_VARS['message'] = f"error, '{nom}' n'existe pas dans la base"
    else:
        res = suppression(SESSION['CONNEXION'], nom)
        if res == 1:
            REQUEST_VARS['message'] = f"succès, suppression de l'équipe '{nom}'"
            # rafraîchir la liste
            REQUEST_VARS['equipes'] = get_equipes(SESSION['CONNEXION'])
        else:
            REQUEST_VARS['message'] = "suppression échouée"