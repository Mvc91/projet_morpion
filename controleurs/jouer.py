from model.morpion_model import get_morpions_equipe, get_equipes
from controleurs.includes import add_activity

add_activity(SESSION['HISTORIQUE'], "jouer une partie normale")

taille_grille = SESSION.get('taille_grille')
nb_tours_max = SESSION.get('nb_tours_max')
equipes1 = SESSION.get('equipes1')
equipes2 = SESSION.get('equipes2')

if not(taille_grille and nb_tours_max and equipes1 and equipes2):
    REQUEST_VARS['message'] = ("error", "Paramétres manquantes allez d'abord choisir.")

else:
    taille_grille = int(taille_grille)
    nb_tours_max = int(nb_tours_max)
    equipes1 = int(equipes1)
    equipes2 = int(equipes2)

    equipes_list = get_equipes(SESSION['CONNEXION'])
    equipes_dict = {e[0]:e[1] for e in equipes_list}

    REQUEST_VARS['morpions1'] = get_morpions_equipe(SESSION['CONNEXION'], equipes1)
    REQUEST_VARS['morpions2'] = get_morpions_equipe(SESSION['CONNEXION'], equipes2)

    if 'partie_jouer' not in SESSION:
        SESSION['partie_jouer'] = {
            'taille_grille': taille_grille,
            'equipes1' : equipes1,
            'equipes2' : equipes2,
            'equipes1_nom':equipes_dict.get(equipes1,'equipes1'),
            'equipes2_nom':equipes_dict.get(equipes2,'equipes2'),
            'tour' : 1,
            'joueur_actuel' : 1,
            'nb_tours_max' : nb_tours_max,
            'grille' : [[None for _ in range(taille_grille)] for _ in range(taille_grille)],
            'morpions_places' : []
        }

    if POST:
        id_morpion = POST.get('id_morpion', None)[0]
        ligne = POST.get('ligne', None)[0]
        colonne = POST.get('colonne', None)[0]

        if id_morpion and ligne and colonne:
            try:
                id_morpion = int(id_morpion)
                ligne = int(ligne)
                colonne = int(colonne)

                if SESSION['partie_jouer']['grille'][ligne][colonne] is None:
                    SESSION['partie_jouer']['grille'][ligne][colonne] = id_morpion
                    SESSION['partie_jouer']['morpions_places'].append((ligne, colonne, id_morpion, SESSION['partie_jouer']['joueur_actuel']))

                    joueur = SESSION['partie_jouer']['joueur_actuel']
                    positions = [(p[0], p[1]) for p in SESSION['partie_jouer']['morpions_places'] if p[3]==joueur]
                    n = SESSION['partie_jouer']['taille_grille']

                    fin = False #pour terminer le jeu 
                    #verification des lignes
                    for l in range(n):
                        if all((l, col) in positions for col in range(n)):
                            nom_gagnant = SESSION['partie_jouer']['equipes1_nom'] if joueur==1 else SESSION['partie_jouer']['equipes2_nom']
                            REQUEST_VARS['message'] = ('victoire', f"🎉🎊 VICTOIRE ! 🎊🎉\n🏆 Félicitations à {nom_gagnant} ! 🏆\n💐🌸🌺 Ligne complète ! 🌺🌸💐")
                            fin = True
                            break

                    #verification des colonnes
                    if not fin:
                        for col in range(n):
                            if all((l, col) in positions for l in range(n)):
                                nom_gagnant = SESSION['partie_jouer']['equipes1_nom'] if joueur==1 else SESSION['partie_jouer']['equipes2_nom']
                                REQUEST_VARS['message'] = ('victoire', f"🎉🎊 VICTOIRE ! 🎊🎉\n🏆 Félicitations à {nom_gagnant} ! 🏆\n💐🌸🌺 Colonne complète ! 🌺🌸💐")
                                fin = True
                                break

                    #verification du diagonale principale
                    if not fin:
                        if all((i, i) in positions for i in range(n)):
                            nom_gagnant = SESSION['partie_jouer']['equipes1_nom'] if joueur==1 else SESSION['partie_jouer']['equipes2_nom']
                            REQUEST_VARS['message'] = ('victoire', f"🎉🎊 VICTOIRE ! 🎊🎉\n🏆 Félicitations à {nom_gagnant} ! 🏆\n💐🌸🌺 Diagonale complète ! 🌺🌸💐")
                            fin = True
    
                    
                    #verification du diagonale secondaire
                    if not fin:
                        if all((i, n-1-i) in positions for i in range(n)):
                            nom_gagnant = SESSION['partie_jouer']['equipes1_nom'] if joueur==1 else SESSION['partie_jouer']['equipes2_nom']
                            REQUEST_VARS['message'] = ('victoire', f"🎉🎊 VICTOIRE ! 🎊🎉\n🏆 Félicitations à {nom_gagnant} ! 🏆\n💐🌸🌺 Diagonale complète ! 🌺🌸💐")
                            fin = True
                    if not fin:
                        if SESSION['partie_jouer']['tour'] >= SESSION['partie_jouer']['nb_tours_max']:
                            REQUEST_VARS['message'] = ('error', f"le nombres des tours max: {SESSION['partie_jouer']['nb_tours_max']} est atteint, match null.")
                            fin = True
                        
                    #échanger le jouer si ya pas encore des gagnants ou les nombres des tours n'est pas encore depasée
                    if not fin:
                        SESSION['partie_jouer']['joueur_actuel'] =2 if SESSION['partie_jouer']['joueur_actuel'] == 1 else 1
                        SESSION['partie_jouer']['tour'] += 1
                        REQUEST_VARS['message'] = ('succés', f"Morpion place en ({ligne}, {colonne})")
                    else:
                        # Partie terminée, on peut réinitialiser pour une nouvelle partie
                        del SESSION['partie_jouer']
                else:
                    REQUEST_VARS['message'] = ('error', f"case occupe choisisez une autre")
            except (ValueError, IndexError) as e:
                 REQUEST_VARS['message'] = ('error', f"Position invalide : {e}")
        else:
            REQUEST_VARS['message'] = ('error', "Données de placement manquantes")
    
    # Mettre à jour la grille affichée seulement si la partie existe encore
    if 'partie_jouer' in SESSION:
        REQUEST_VARS['grille'] = SESSION['partie_jouer']['grille']
        REQUEST_VARS['partie'] = SESSION['partie_jouer']

        if not POST:
            REQUEST_VARS['message'] = ('info', f"Tour {SESSION['partie_jouer']['tour']} / {SESSION['partie_jouer']['nb_tours_max']} — C'est au tour de {SESSION['partie_jouer']['equipes1_nom'] if SESSION['partie_jouer']['joueur_actuel']==1 else SESSION['partie_jouer']['equipes2_nom']}")
