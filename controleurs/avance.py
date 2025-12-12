from model.morpion_model import (get_morpions_equipe, get_equipes, creer_partie, 
                                 terminer_partie, ajouter_action_journal)
from controleurs.includes import add_activity
import random

add_activity(SESSION['HISTORIQUE'], "jouer une partie avancée")

taille_grille = SESSION.get('taille_grille')
nb_tours_max = SESSION.get('nb_tours_max')
id_configuration = SESSION.get('id_configuration')
equipes1 = SESSION.get('equipes1')
equipes2 = SESSION.get('equipes2')

if not(taille_grille and nb_tours_max and equipes1 and equipes2):
    REQUEST_VARS['message'] = ("error", "Paramètres manquants, allez d'abord choisir.")

else:
    taille_grille = int(taille_grille)
    nb_tours_max = int(nb_tours_max)
    id_configuration = int(id_configuration) if id_configuration else 1
    equipes1 = int(equipes1)
    equipes2 = int(equipes2)

    equipes_list = get_equipes(SESSION['CONNEXION'])
    equipes_dict = {e[0]:e[1] for e in equipes_list}

    morpions1_base = get_morpions_equipe(SESSION['CONNEXION'], equipes1)
    morpions2_base = get_morpions_equipe(SESSION['CONNEXION'], equipes2)

    # Initialisation de la partie avancée
    if 'partie_avancee' not in SESSION:
        # Créer la partie en base de données
        id_partie = creer_partie(SESSION['CONNEXION'], equipes1, equipes2, id_configuration)
        SESSION['CONNEXION'].commit()
        
        SESSION['partie_avancee'] = {
            'id_partie': id_partie,
            'taille_grille': taille_grille,
            'equipes1': equipes1,
            'equipes2': equipes2,
            'equipes1_nom': equipes_dict.get(equipes1, 'Équipe 1'),
            'equipes2_nom': equipes_dict.get(equipes2, 'Équipe 2'),
            'tour': 1,
            'joueur_actuel': 1,
            'nb_tours_max': nb_tours_max,
            'grille': [[None for _ in range(taille_grille)] for _ in range(taille_grille)],
            'cases_detruites': set(),
            'morpions_etat': {},
            'numero_action': 1
        }

    partie = SESSION['partie_avancee']
    REQUEST_VARS['morpions1'] = morpions1_base
    REQUEST_VARS['morpions2'] = morpions2_base

    # Fonction pour enregistrer une action dans le journal
    def enregistrer_action(texte):
        """Enregistre une action dans le journal de la partie"""
        try:
            ajouter_action_journal(SESSION['CONNEXION'], partie['id_partie'], 
                                 partie['numero_action'], texte)
            SESSION['CONNEXION'].commit()
            partie['numero_action'] += 1
        except Exception as e:
            pass  # Ignorer les erreurs d'enregistrement

    # Fonction pour vérifier si un morpion peut agir
    def peut_agir(joueur):
        """Vérifie si le joueur a au moins un morpion vivant sur la grille"""
        for morpion_id, etat in partie['morpions_etat'].items():
            if etat['equipe'] == joueur and etat['pv'] > 0 and etat['ligne'] is not None:
                return True
        return False

    # Fonction pour vérifier la victoire
    def verifier_victoire():
        """Retourne (gagnant, raison) ou (None, None) si pas de gagnant"""
        n = partie['taille_grille']
        
        # Vérifier si tous les morpions adverses sont morts
        morpions_vivants = {1: [], 2: []}
        morpions_morts = {1: 0, 2: 0}
        
        for morpion_id, etat in partie['morpions_etat'].items():
            if etat['ligne'] is not None:  # A été placé sur la grille
                if etat['pv'] > 0:
                    pos = (etat['ligne'], etat['col'])
                    morpions_vivants[etat['equipe']].append(pos)
                else:
                    morpions_morts[etat['equipe']] += 1
        
        # Vérifier si tous les morpions placés d'une équipe sont morts (seulement si les deux équipes ont placé au moins 1 morpion)
        equipe1_a_place = len(morpions_vivants[1]) + morpions_morts[1] > 0
        equipe2_a_place = len(morpions_vivants[2]) + morpions_morts[2] > 0
        
        if equipe1_a_place and equipe2_a_place:
            if len(morpions_vivants[1]) == 0 and len(morpions_vivants[2]) > 0:
                return (2, "Tous les morpions de l'équipe 1 sont morts ! 💀")
            if len(morpions_vivants[2]) == 0 and len(morpions_vivants[1]) > 0:
                return (1, "Tous les morpions de l'équipe 2 sont morts ! 💀")
        
        # Vérifier alignements (seulement si l'équipe a au moins n morpions)
        for equipe in [1, 2]:
            positions = morpions_vivants[equipe]
            
            # Il faut au moins n morpions pour gagner
            if len(positions) < n:
                continue
            
            # Lignes
            for l in range(n):
                if all((l, col) in positions for col in range(n)):
                    return (equipe, "Ligne complète ! ➡️")
            
            # Colonnes
            for col in range(n):
                if all((l, col) in positions for l in range(n)):
                    return (equipe, "Colonne complète ! ⬇️")
            
            # Diagonale principale
            if all((i, i) in positions for i in range(n)):
                return (equipe, "Diagonale complète ! ↘️")
            
            # Diagonale secondaire
            if all((i, n-1-i) in positions for i in range(n)):
                return (equipe, "Diagonale complète ! ↙️")
        
        # Vérifier si un joueur ne peut plus agir (seulement si les deux équipes ont au moins 1 morpion placé)
        a_morpions_equipe1 = len(morpions_vivants[1]) > 0
        a_morpions_equipe2 = len(morpions_vivants[2]) > 0
        
        if a_morpions_equipe1 and a_morpions_equipe2:
            if not peut_agir(1) and peut_agir(2):
                return (2, "L'équipe 1 ne peut plus agir ! 🚫")
            if not peut_agir(2) and peut_agir(1):
                return (1, "L'équipe 2 ne peut plus agir ! 🚫")
        
        return (None, None)

    # Traitement des actions POST
    if POST:
        action_type = POST.get('action_type', [None])[0]
        
        if action_type == 'placer':
            id_morpion = POST.get('id_morpion', [None])[0]
            ligne = POST.get('ligne', [None])[0]
            colonne = POST.get('colonne', [None])[0]
            
            if id_morpion and ligne is not None and colonne is not None:
                try:
                    id_morpion = int(id_morpion)
                    ligne = int(ligne)
                    colonne = int(colonne)
                    
                    # Vérifications
                    if ligne < 0 or ligne >= taille_grille or colonne < 0 or colonne >= taille_grille:
                        REQUEST_VARS['message'] = ('error', "Position hors de la grille !")
                    elif (ligne, colonne) in partie['cases_detruites']:
                        REQUEST_VARS['message'] = ('error', "Cette case a été détruite ! ☠️")
                    elif partie['grille'][ligne][colonne] is not None:
                        REQUEST_VARS['message'] = ('error', "Case occupée !")
                    elif id_morpion in partie['morpions_etat']:
                        REQUEST_VARS['message'] = ('error', "Ce morpion est déjà sur la grille !")
                    else:
                        # Récupérer les stats du morpion
                        morpion_data = None
                        if partie['joueur_actuel'] == 1:
                            for m in morpions1_base:
                                if m[0] == id_morpion:
                                    morpion_data = m
                                    break
                        else:
                            for m in morpions2_base:
                                if m[0] == id_morpion:
                                    morpion_data = m
                                    break
                        
                        if morpion_data:
                            # Placer le morpion
                            partie['grille'][ligne][colonne] = id_morpion
                            partie['morpions_etat'][id_morpion] = {
                                'nom': morpion_data[1],
                                'pv': morpion_data[3],
                                'pv_max': morpion_data[3],
                                'attaque': morpion_data[4],
                                'mana': morpion_data[5],
                                'mana_max': morpion_data[5],
                                'reussite': morpion_data[6],
                                'equipe': partie['joueur_actuel'],
                                'ligne': ligne,
                                'col': colonne
                            }
                            
                            texte_action = f"Tour {partie['tour']}: {morpion_data[1]} (Équipe {partie['joueur_actuel']}) placé en ({ligne}, {colonne})"
                            enregistrer_action(texte_action)
                            REQUEST_VARS['message'] = ('success', f"✅ {morpion_data[1]} placé en ({ligne}, {colonne})")
                            
                            # Changer de joueur
                            partie['joueur_actuel'] = 2 if partie['joueur_actuel'] == 1 else 1
                            partie['tour'] += 1
                        else:
                            REQUEST_VARS['message'] = ('error', "Morpion invalide !")
                            
                except (ValueError, IndexError) as e:
                    REQUEST_VARS['message'] = ('error', f"Erreur: {e}")

        #ensuite il faut verifier le post de l'attaque 
        elif action_type == 'attaquer':
            id_attaquant = POST.get('id_attaquant', [None])[0]
            id_cible = POST.get('id_cible', [None])[0]
            
            if id_attaquant and id_cible:
                try:
                    id_attaquant = int(id_attaquant)
                    id_cible = int(id_cible)
                    
                    attaquant = partie['morpions_etat'].get(id_attaquant)
                    cible = partie['morpions_etat'].get(id_cible)
                    
                    if not attaquant or not cible:
                        REQUEST_VARS['message'] = ('error', "Morpion invalide !")
                    elif attaquant['equipe'] != partie['joueur_actuel']:
                        REQUEST_VARS['message'] = ('error', "Ce n'est pas votre morpion !")
                    elif attaquant['pv'] <= 0:
                        REQUEST_VARS['message'] = ('error', "Ce morpion est mort ! 💀")
                    elif cible['pv'] <= 0:
                        REQUEST_VARS['message'] = ('error', "La cible est déjà morte ! 💀")
                    elif attaquant['equipe'] == cible['equipe']:
                        REQUEST_VARS['message'] = ('error', "Pas d'attaque entre alliés ! 🛡️")
                    else:
                        # Vérifier adjacence (horizontale ou verticale)
                        dist_l = abs(attaquant['ligne'] - cible['ligne'])
                        dist_c = abs(attaquant['col'] - cible['col'])
                        
                        if not ((dist_l == 1 and dist_c == 0) or (dist_l == 0 and dist_c == 1)):
                            REQUEST_VARS['message'] = ('error', "La cible doit être adjacente (horizontal/vertical) ! ↔️↕️")
                        else:
                            # Test de réussite
                            proba_reussite = min(100, attaquant['reussite'] * 10)
                            tirage = random.randint(0, 100)
                            
                            if tirage <= proba_reussite:
                                # Attaque réussie
                                degats = attaquant['attaque']
                                cible['pv'] = max(0, cible['pv'] - degats)
                                attaquant['reussite'] += 0.5
                                
                                msg = f"⚔️ {attaquant['nom']} attaque {cible['nom']} et inflige {degats} dégâts !"
                                
                                if cible['pv'] <= 0:
                                    # Morpion mort, libérer la case
                                    partie['grille'][cible['ligne']][cible['col']] = None
                                    cible['ligne'] = None
                                    cible['col'] = None
                                    msg += f" 💀 {cible['nom']} est mort !"
                                else:
                                    msg += f" (PV restants: {cible['pv']})"
                                
                                texte_action = f"Tour {partie['tour']}: {msg}"
                                enregistrer_action(texte_action)
                                REQUEST_VARS['message'] = ('success', msg)
                            else:
                                texte_action = f"Tour {partie['tour']}: {attaquant['nom']} rate son attaque ! ❌"
                                enregistrer_action(texte_action)
                                REQUEST_VARS['message'] = ('error', f"❌ Attaque ratée ! (Réussite: {proba_reussite}%, Tirage: {tirage})")
                            
                            # Changer de joueur
                            partie['joueur_actuel'] = 2 if partie['joueur_actuel'] == 1 else 1
                            partie['tour'] += 1
                            
                except (ValueError, IndexError) as e:
                    REQUEST_VARS['message'] = ('error', f"Erreur: {e}")
        
        elif action_type == 'sort':
            id_lanceur = POST.get('id_lanceur', [None])[0]
            id_cible = POST.get('id_cible', [None])[0]
            sort_type = POST.get('sort_type', [None])[0]
            
            if id_lanceur and id_cible and sort_type:
                try:
                    id_lanceur = int(id_lanceur)
                    id_cible = int(id_cible)
                    
                    lanceur = partie['morpions_etat'].get(id_lanceur)
                    cible = partie['morpions_etat'].get(id_cible)
                    
                    if not lanceur:
                        REQUEST_VARS['message'] = ('error', "Lanceur invalide !")
                    elif lanceur['equipe'] != partie['joueur_actuel']:
                        REQUEST_VARS['message'] = ('error', "Ce n'est pas votre morpion !")
                    elif lanceur['pv'] <= 0:
                        REQUEST_VARS['message'] = ('error', "Ce morpion est mort ! 💀")
                    else:
                        # Définir les coûts et effets des sorts
                        sorts_info = {
                            'boule_feu': {'cout': 2, 'nom': 'Boule de feu', 'emoji': '🔥'},
                            'soin': {'cout': 1, 'nom': 'Sort de soin', 'emoji': '💚'},
                            'armageddon': {'cout': 5, 'nom': 'Armageddon', 'emoji': '💥'}
                        }
                        
                        if sort_type not in sorts_info:
                            REQUEST_VARS['message'] = ('error', "Sort invalide !")
                        else:
                            sort_info = sorts_info[sort_type]
                            cout_mana = sort_info['cout']
                            
                            if lanceur['mana'] < cout_mana:
                                REQUEST_VARS['message'] = ('error', f"Pas assez de mana ! (requis: {cout_mana}, disponible: {lanceur['mana']}) 🔮")
                            else:
                                # Déduire le mana
                                lanceur['mana'] -= cout_mana
                                
                                # Test de réussite
                                proba_reussite = min(100, lanceur['reussite'] * 10)
                                tirage = random.randint(0, 100)
                                
                                if tirage <= proba_reussite:
                                    # Sort réussi
                                    lanceur['reussite'] += 0.5
                                    
                                    if sort_type == 'boule_feu':
                                        if not cible:
                                            REQUEST_VARS['message'] = ('error', "Cible invalide !")
                                        elif cible['pv'] <= 0:
                                            REQUEST_VARS['message'] = ('error', "La cible est déjà morte ! 💀")
                                        elif lanceur['equipe'] == cible['equipe']:
                                            REQUEST_VARS['message'] = ('error', "Pas d'attaque entre alliés ! 🛡️")
                                        else:
                                            cible['pv'] = max(0, cible['pv'] - 3)
                                            msg = f"{sort_info['emoji']} {lanceur['nom']} lance {sort_info['nom']} sur {cible['nom']} ! -3 PV"
                                            
                                            if cible['pv'] <= 0:
                                                partie['grille'][cible['ligne']][cible['col']] = None
                                                cible['ligne'] = None
                                                cible['col'] = None
                                                msg += f" 💀 {cible['nom']} est mort !"
                                            else:
                                                msg += f" (PV restants: {cible['pv']})"
                                            
                                            texte_action = f"Tour {partie['tour']}: {msg}"
                                            enregistrer_action(texte_action)
                                            REQUEST_VARS['message'] = ('success', msg)
                                            
                                            partie['joueur_actuel'] = 2 if partie['joueur_actuel'] == 1 else 1
                                            partie['tour'] += 1
                                    
                                    elif sort_type == 'soin':
                                        if not cible:
                                            REQUEST_VARS['message'] = ('error', "Cible invalide !")
                                        elif cible['pv'] <= 0:
                                            REQUEST_VARS['message'] = ('error', "Impossible de soigner un morpion mort ! 💀")
                                        elif lanceur['equipe'] != cible['equipe']:
                                            REQUEST_VARS['message'] = ('error', "Impossible de soigner un ennemi ! ⚔️")
                                        else:
                                            cible['pv'] = min(cible['pv_max'], cible['pv'] + 2)
                                            msg = f"{sort_info['emoji']} {lanceur['nom']} soigne {cible['nom']} ! +2 PV (PV: {cible['pv']}/{cible['pv_max']})"
                                            
                                            texte_action = f"Tour {partie['tour']}: {msg}"
                                            enregistrer_action(texte_action)
                                            REQUEST_VARS['message'] = ('success', msg)
                                            
                                            partie['joueur_actuel'] = 2 if partie['joueur_actuel'] == 1 else 1
                                            partie['tour'] += 1
                                    
                                    elif sort_type == 'armageddon':
                                        if not cible:
                                            REQUEST_VARS['message'] = ('error', "Cible invalide !")
                                        else:
                                            # Vérifier pas kamikaze
                                            if cible['ligne'] == lanceur['ligne'] and cible['col'] == lanceur['col']:
                                                REQUEST_VARS['message'] = ('error', "Pas de suicide ! 🚫💀")
                                            else:
                                                ligne_cible = cible['ligne']
                                                col_cible = cible['col']
                                                
                                                # Tuer le morpion sur la case
                                                if cible['pv'] > 0:
                                                    cible['pv'] = 0
                                                    partie['grille'][ligne_cible][col_cible] = None
                                                    cible['ligne'] = None
                                                    cible['col'] = None
                                                
                                                # Détruire la case
                                                partie['cases_detruites'].add((ligne_cible, col_cible))
                                                
                                                msg = f"{sort_info['emoji']} {lanceur['nom']} lance Armageddon ! Case ({ligne_cible}, {col_cible}) détruite ! ☠️"
                                                texte_action = f"Tour {partie['tour']}: {msg}"
                                                enregistrer_action(texte_action)
                                                REQUEST_VARS['message'] = ('success', msg)
                                                
                                                partie['joueur_actuel'] = 2 if partie['joueur_actuel'] == 1 else 1
                                                partie['tour'] += 1
                                else:
                                    texte_action = f"Tour {partie['tour']}: {lanceur['nom']} rate son sort ! ❌"
                                    enregistrer_action(texte_action)
                                    REQUEST_VARS['message'] = ('error', f"❌ Sort raté ! (Réussite: {proba_reussite}%, Tirage: {tirage})")
                                    
                                    partie['joueur_actuel'] = 2 if partie['joueur_actuel'] == 1 else 1
                                    partie['tour'] += 1
                                    
                except (ValueError, IndexError) as e:
                    REQUEST_VARS['message'] = ('error', f"Erreur: {e}")

    # Vérification de fin de partie
    if 'partie_avancee' in SESSION:
        gagnant, raison = verifier_victoire()
        
        if gagnant:
            nom_gagnant = partie['equipes1_nom'] if gagnant == 1 else partie['equipes2_nom']
            id_equipe_gagnante = partie['equipes1'] if gagnant == 1 else partie['equipes2']
            
            # Terminer la partie en base de données
            terminer_partie(SESSION['CONNEXION'], partie['id_partie'], id_equipe_gagnante)
            SESSION['CONNEXION'].commit()
            
            REQUEST_VARS['message'] = ('victoire', f"🎉🎊 VICTOIRE ! 🎊🎉\n🏆 Félicitations à {nom_gagnant} ! 🏆\n💐🌸🌺 {raison} 🌺🌸💐")
            REQUEST_VARS['partie_terminee'] = True
            
            # Supprimer la session de partie
            del SESSION['partie_avancee']
            
        elif partie['tour'] > partie['nb_tours_max']:
            # Match nul
            terminer_partie(SESSION['CONNEXION'], partie['id_partie'], None)
            SESSION['CONNEXION'].commit()
            
            REQUEST_VARS['message'] = ('error', f"⏱️ Nombre maximum de tours atteint ({partie['nb_tours_max']}) ! Match nul. 🤝")
            REQUEST_VARS['partie_terminee'] = True
            
            # Supprimer la session de partie
            del SESSION['partie_avancee']
        
        if 'partie_avancee' in SESSION:
            REQUEST_VARS['grille'] = partie['grille']
            REQUEST_VARS['partie'] = partie
#j'ai plus des neurones!!