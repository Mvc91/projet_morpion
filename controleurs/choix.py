from model.morpion_model import get_configuration, get_equipes
from controleurs.includes import add_activity

add_activity(SESSION['HISTORIQUE'], "choix des equipes et nb_tours et la grille")

REQUEST_VARS['configuration'] = get_configuration(SESSION['CONNEXION'])
REQUEST_VARS['equipes'] = get_equipes(SESSION['CONNEXION'])



if POST:
    SESSION['id_configuration'] = POST.get('id_configuration', [None])[0]
    SESSION['nb_tours_max'] = POST.get('nb_tours_max', [None])[0]
    SESSION['taille_grille'] = POST.get('taille_grille', [None])[0]
    SESSION['equipes1'] = POST.get('equipes1', [None])[0]
    SESSION['equipes2'] = POST.get('equipes2', [None])[0]
    if SESSION['nb_tours_max'] is not None and SESSION['taille_grille'] is not None:
        REQUEST_VARS['message'] = f"bien recu, '{SESSION['nb_tours_max']}' et '{SESSION['taille_grille']}'"
    else:
        REQUEST_VARS['message'] = "is none"

 

