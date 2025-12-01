from model.morpion_model import nombres_instances, top_equipes, duree_partie
from controleurs.includes import add_activity

add_activity(SESSION['HISTORIQUE'], "accueil projet_morpion")

REQUEST_VARS['morpions'] = nombres_instances(SESSION['CONNEXION'], 'morpions')
REQUEST_VARS['equipes'] = nombres_instances(SESSION['CONNEXION'], 'equipes')
REQUEST_VARS['parties'] = nombres_instances(SESSION['CONNEXION'], 'parties')

REQUEST_VARS['top'] = top_equipes(SESSION['CONNEXION'])

REQUEST_VARS['duree'] = duree_partie(SESSION['CONNEXION']) 