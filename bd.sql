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
	CHECK(points_attaque + points_mana + points_reussite + points_vie ) = 15
);

CREATE TABLE equipes (
	id_equipe     SERIAL PRIMARY KEY,
	nom           VARCHAR(60) NOT NULL UNIQUE,
	couleur       VARCHAR(32) NOT NULL UNIQUE, 
	date_creation DATE NOT NULL
);

CREATE TABLE equipes_morpions (
	id_equipe   INT NOT NULL REFERENCES equipes(id_equipe),
	id_morpion  INT NOT NULL REFERENCES morpions(id_morpion),
	PRIMARY KEY (id_equipe, id_morpion)
);

CREATE table configurations (
	id_configuration SERIAL PRIMARY key,
	taille_grille INT NOT NULL CHECK(taille_grille >= 3),
	nb_tours_max INT NOT NULL
);

CREATE TABLE parties (
	id_partie          SERIAL PRIMARY KEY,
	id_equipe_a        INT NOT NULL REFERENCES equipes(id_equipe) ON DELETE RESTRICT,
	id_equipe_b        INT NOT NULL REFERENCES equipes(id_equipe) ON DELETE RESTRICT,
	date_debut         DATE NOT NULL,
	date_fin           DATE NULL,
	id_equipe_gagnante INT NULL REFERENCES equipes(id_equipe) ON DELETE SET NULL
);
