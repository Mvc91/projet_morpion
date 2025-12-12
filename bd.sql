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
	id_configuration   INT NOT NULL REFERENCES configurations(id_configuration) ON DELETE CASCADE,
	date_debut         TIMESTAMP NOT NULL,
	date_fin           TIMESTAMP NULL,
	id_equipe_gagnante INT NULL REFERENCES equipes(id_equipe) ON DELETE SET NULL
);

CREATE TABLE journal (
	id_partie        INT NOT NULL REFERENCES parties(id_partie) ON DELETE CASCADE,
	numero_action    INT NOT NULL,
	date_action      TIMESTAMP NOT NULL,
	texte_action     TEXT NOT NULL,
	PRIMARY KEY (id_partie, numero_action)
);

-- =====================
-- Données d'exemple
-- =====================

-- Morpions (somme des points = 15)
INSERT INTO morpions (nom, image, points_vie, points_attaque, points_mana, points_reussite) VALUES
	('Pyro',   'static/img/t1.png',   1, 1, 3, 10),
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
	('Les Dragons de Feu',    '#ff4757', '2024-10-01'),
	('Les Gardiens du Cristal', '#1e90ff', '2024-10-05'),
	('Les Chasseurs d''Ombre',  '#2ed573', '2024-10-10'),
	('Les Titans de l''Orage',  '#ffa502', '2024-10-12'),
	('Les Maîtres de Glace',   '#9b59b6', '2024-10-15'),
	('Les Guerriers de Lumière', '#e67e22', '2024-10-18');

-- Configurations
INSERT INTO configurations (taille_grille, nb_tours_max) VALUES
	(3, 9),
	(4, 12),
	(4, 16);

-- Composition des équipes (chaque équipe a entre 6 et 8 morpions différents)
-- Équipe 1: Les Dragons de Feu (8 morpions)
INSERT INTO equipes_morpions (id_equipe, id_morpion) VALUES
	(1, 1), (1, 2), (1, 3), (1, 9), (1, 12), (1, 14), (1, 15), (1, 7),
-- Équipe 2: Les Gardiens du Cristal (7 morpions)
	(2, 2), (2, 4), (2, 5), (2, 8), (2, 10), (2, 11), (2, 13),
-- Équipe 3: Les Chasseurs d'Ombre (6 morpions)
	(3, 1), (3, 5), (3, 6), (3, 11), (3, 16), (3, 3),
-- Équipe 4: Les Titans de l'Orage (8 morpions)
	(4, 3), (4, 4), (4, 6), (4, 7), (4, 9), (4, 14), (4, 15), (4, 16),
-- Équipe 5: Les Maîtres de Glace (7 morpions)
	(5, 1), (5, 8), (5, 10), (5, 12), (5, 13), (5, 2), (5, 5),
-- Équipe 6: Les Guerriers de Lumière (6 morpions)
	(6, 4), (6, 6), (6, 7), (6, 9), (6, 11), (6, 14);

-- Parties (dates et gagnants facultatifs)
-- Dragons de Feu vs Gardiens du Cristal, gagnant Dragons de Feu
INSERT INTO parties (id_equipe_a, id_equipe_b, id_configuration, date_debut, date_fin, id_equipe_gagnante) VALUES
	( 1, 2, 1, '2024-11-01 10:00:00', '2024-11-01 10:30:00', 1),
-- Gardiens du Cristal vs Chasseurs d'Ombre, gagnant Gardiens du Cristal
	( 2, 3, 1, '2024-11-02 14:00:00', '2024-11-02 14:25:00', 2),
-- Chasseurs d'Ombre vs Titans de l'Orage, égalité (pas de gagnant)
	( 3, 4, 2, '2024-11-03 09:00:00', NULL, NULL),
-- Dragons de Feu vs Titans de l'Orage, gagnant Titans de l'Orage
	( 1, 4, 1, '2024-11-04 16:00:00', '2024-11-05 16:45:00', 4),
-- Maîtres de Glace vs Guerriers de Lumière, gagnant Maîtres de Glace
	( 5, 6, 2, '2024-11-06 11:00:00', '2024-11-06 11:40:00', 5);

-- Exemples de journal d'actions
INSERT INTO journal (id_partie, numero_action, date_action, texte_action) VALUES
	(1, 1, '2024-11-01 10:01:00', 'Pyro placé en (0, 0)'),
	(1, 2, '2024-11-01 10:02:00', 'Aqua placé en (1, 1)'),
	(1, 3, '2024-11-01 10:03:00', 'Pyro attaque Aqua et inflige 5 dégâts');
