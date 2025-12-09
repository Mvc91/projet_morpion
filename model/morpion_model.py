import psycopg
from psycopg import sql
from logzero import logger

def execute_select_query(connexion, query, params=[]):
    with connexion.cursor() as curseur:
        try:
            curseur.execute(query, params)
            resultat = curseur.fetchall()
            return resultat
        except psycopg.Error as e:
            logger.error(e)
    return None

def execute_other_query(connexion, query, params=[]):
    """
    Méthode générique pour exécuter une requête INSERT, UPDATE, DELETE.
    Utilisée par des fonctions plus spécifiques.
    """
    with connexion.cursor() as cursor:
        try:
            cursor.execute(query, params)
            result = cursor.rowcount
            return result 
        except psycopg.Error as e:
            logger.error(e)
    return None

#les fonctions pour l'accueil

def nombres_instances(connexion, nom_table):
    query = sql.SQL('SELECT COUNT(*) FROM {table}').format(table=sql.Identifier(nom_table),)
    return execute_select_query(connexion, query)


def top_equipes(connexion):
    query = """SELECT e.nom, COUNT(*) AS wins
                FROM parties p
                JOIN equipes e ON e.id_equipe = p.id_equipe_gagnante
                WHERE p.id_equipe_gagnante IS NOT NULL
                GROUP BY e.id_equipe, e.nom
                ORDER BY wins DESC, e.nom ASC
                LIMIT 3;"""
    return execute_select_query(connexion, query)

def duree_partie(connexion):
        query = """
                SELECT
                    id_partie,
                    MIN(date_fin - date_debut) AS duree_plus_rapide,
                    MAX(date_fin - date_debut) AS duree_plus_longue
                FROM parties
                WHERE date_fin IS NOT NULL
                group by id_partie;
        """
        return execute_select_query(connexion, query)

#les fonctions pour la creation

def get_morpions(connexion):
    query = "select id_morpion, nom, image from morpions order by nom;"
    return execute_select_query(connexion, query)

def creer_equipe(connexion, nom, couleur):
    query = """ insert into equipes (nom, couleur, date_creation) 
                values (%s, %s, NOW());"""
    return execute_other_query(connexion, query, [nom, couleur])

def ajout_morpion_equipe(connexion, id_equipe, id_morpion):
    query = """insert into equipes_morpions(id_equipe, id_morpion)
                values (%s, %s);"""
    return execute_other_query(connexion, query, [id_equipe, id_morpion])

def get_equipes(connexion):
    query = "select id_equipe, nom from equipes order by nom;"
    return execute_select_query(connexion, query)

def dernier_id_equipe(connexion):
    query = "select max(id_equipe) from equipes;"
    return execute_select_query(connexion, query)

#les fontions pour la suppression

def suppression (connexion, nom):
    query = "delete from equipes where nom=%s"
    return execute_other_query(connexion, query, [nom])

#les fonctions pour jouer une partie normale

def get_configuration(connexion):
    query = "select id_configuration, taille_grille, nb_tours_max from configurations;"
    return execute_select_query(connexion, query)
 

def get_morpions_equipe(connexion, id_equipe):
    """Retourne les morpions d'une équipe donnée."""
    query = """SELECT m.id_morpion, m.nom, m.image, m.points_vie, m.points_attaque, m.points_mana, m.points_reussite
               FROM morpions m
               JOIN equipes_morpions em ON m.id_morpion = em.id_morpion
               WHERE em.id_equipe = %s
               ORDER BY m.nom;"""
    return execute_select_query(connexion, query, [id_equipe])

