DROP SCHEMA IF EXISTS projet CASCADE;
CREATE SCHEMA IF NOT EXISTS projet;
SET SEARCH_PATH TO projet;

CREATE TABLE morpions (
	id_morpion       SERIAL PRIMARY KEY,
	nom              VARCHAR(50) NOT NULL UNIQUE,
	image            VARCHAR(255) NOT NULL,
	points_vie       SMALLINT NOT NULL,
	points_attaque   SMALLINT NOT NULL,
	points_mana      SMALLINT NOT NULL,
	points_reussite  SMALLINT NOT NULL,
	CHECK (points_attaque + points_mana + points_reussite + points_vie = 15)
);
 
CREATE TABLE equipes (
	id_equipe     SERIAL PRIMARY KEY,
	nom           VARCHAR(60) NOT NULL UNIQUE,
	couleur       VARCHAR(32) NOT NULL UNIQUE, 
	date_creation DATE NOT NULL
);

CREATE TABLE equipes_morpions (
	id_equipe   INT NOT NULL REFERENCES equipes(id_equipe) on DELETE CASCADE,
	id_morpion  INT NOT NULL REFERENCES morpions(id_morpion) on delete CASCADE,
	PRIMARY KEY (id_equipe, id_morpion)
);

CREATE table configurations (
	id_configuration SERIAL PRIMARY key,
	taille_grille INT NOT NULL CHECK(taille_grille >= 3),
	nb_tours_max INT NOT NULL
);

CREATE TABLE parties (
	id_partie          SERIAL PRIMARY KEY,
	id_equipe_a        INT NOT NULL REFERENCES equipes(id_equipe) ON DELETE CASCADE,
	id_equipe_b        INT NOT NULL REFERENCES equipes(id_equipe) ON DELETE CASCADE,
	date_debut         DATE NOT NULL,
	date_fin           DATE NULL,
	id_equipe_gagnante INT NULL REFERENCES equipes(id_equipe) ON DELETE SET NULL
);

-- =====================
-- Données d'exemple
-- =====================

-- Morpions (somme des points = 15)
INSERT INTO morpions (nom, image, points_vie, points_attaque, points_mana, points_reussite) VALUES
	('Pyro',   'static/img/t1.png',   4, 5, 3, 3),
	('Aqua',   'static/img/t2.png',   5, 3, 4, 3),
	('Terra',  'static/img/t3.png',  6, 2, 3, 4),
	('Volt',   'static/img/t4.png',   3, 6, 3, 3),
	('Lumen',  'static/img/t5.png',  4, 4, 4, 3),
	('Umbra',  'static/img/t6.png',  5, 4, 2, 4),
	('Zephyr', 'static/img/t7.png',  4, 5, 2, 4),
	('Glacia', 'static/img/t8.png',  5, 2, 5, 3),
	('Ignis',  'static/img/t9.png',  3, 6, 2, 4),
	('Aeris',  'static/img/t10.png', 4, 3, 5, 3),
	('Noctis', 'static/img/t11.png', 6, 3, 2, 4),
	('Solis',  'static/img/t12.png', 5, 5, 1, 4),
	('Flora',  'static/img/t13.png', 6, 2, 4, 3),
	('Cryo',   'static/img/t14.png', 4, 4, 3, 4),
	('Electra','static/img/t15.png', 3, 6, 3, 3),
	('Umbris', 'static/img/t16.png', 5, 3, 3, 4);

-- Équipes
INSERT INTO equipes (nom, couleur, date_creation) VALUES
	('Alpha',   '#ff4757', '2024-10-01'),
	('Bravo',   '#1e90ff', '2024-10-05'),
	('Charlie', '#2ed573', '2024-10-10'),
	('Delta',   '#ffa502', '2024-10-12');

-- Configurations
INSERT INTO configurations (taille_grille, nb_tours_max) VALUES
	(3, 9),
	(4, 12),
	(4, 16);

-- Composition des équipes (6 morpions disponibles, on en affecte 3 par équipe)
-- On suppose que les id auto-incrémentés commencent à 1 selon l'ordre d'insertion ci-dessus.
INSERT INTO equipes_morpions (id_equipe, id_morpion) VALUES
	(1, 1), (1, 2), (1, 3),
	(2, 2), (2, 4), (2, 5),
	(3, 1), (3, 5), (3, 6),
	(4, 3), (4, 4), (4, 6);

-- Parties (dates et gagnants facultatifs)
-- Alpha vs Bravo, gagnant Alpha
INSERT INTO parties (id_equipe_a, id_equipe_b, date_debut, date_fin, id_equipe_gagnante) VALUES
	( 1, 2, '2024-11-01', '2024-11-01', 1),
-- Bravo vs Charlie, gagnant Bravo
	( 2, 3, '2024-11-02', '2024-11-02', 2),
-- Charlie vs Delta, égalité (pas de gagnant)
	( 3, 4, '2024-11-03', NULL, NULL),
-- Alpha vs Delta, gagnant Delta
	( 1, 4, '2024-11-04', '2024-11-05', 4);
