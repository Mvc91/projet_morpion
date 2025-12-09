from model.morpion_model import creer_equipe, get_morpions, ajout_morpion_equipe, dernier_id_equipe

# Charger la liste des morpions pour le formulaire
REQUEST_VARS['morpions'] = get_morpions(SESSION['CONNEXION'])

# Lecture simple du POST (dict de listes)
nom = POST.get('nom', [''])[0].strip()
couleur = POST.get('couleur', [''])[0].strip()
coches = POST.get('morpions', [])

# Si nom et couleur sont fournis, on traite la création
if nom and couleur:
	if len(coches) < 6 or len(coches) > 8:
		REQUEST_VARS['message'] = ('error', 'Sélectionnez entre 6 et 8 morpions.')
	else:
		res = creer_equipe(SESSION['CONNEXION'], nom, couleur)
		if res == 1:
			last = dernier_id_equipe(SESSION['CONNEXION'])
			if last and last[0] and last[0][0]:
				id_equipe = int(last[0][0])
				ok = 0
				for v in coches:
					try:
						ok += (ajout_morpion_equipe(SESSION['CONNEXION'], id_equipe, int(v)) or 0)
					except ValueError:
						pass
				REQUEST_VARS['message'] = ('success', f"Équipe '{nom}' créée avec {ok} morpions.")
			else:
				REQUEST_VARS['message'] = ('error', "Impossible de récupérer l'id de l'équipe.")
		else:
			REQUEST_VARS['message'] = ('error', "Création échouée (nom/couleur déjà utilisés ?)")

 