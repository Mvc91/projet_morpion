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

def nombres_instances(connexion, nom_table):
    query = sql.SQL('SELECT COUNT(*) FROM {table}').format(table=sql.Identifier(nom_table),)
    return execute_select_query(connexion, query)


def top_equipes(connexion):
    query = "SELECT nom  from equipes where id_equipe IN (select id_equipe_gagnante from parties order by id_equipe_gagnante desc limit 3)"
    return execute_select_query(connexion, query)

def duree_partie(connexion):
    query = """select id_partie, min(date_debut - date_fin) as "la plus rapide", max(date_debut - date_fin) as "la plus longue" from parties group by id_partie"""
    return execute_select_query(connexion, query)

 