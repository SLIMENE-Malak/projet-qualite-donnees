-- Création des tables sources (s1 à s4), recréées à chaque chargement.
-- Codes et identifiants en TEXT : un code postal mal formé (ex. '999') doit être
-- chargé tel quel pour être mesuré par l'audit de conformité.
-- Mesures numériques en NUMERIC : nécessaires aux calculs des tables cibles.
CREATE SCHEMA IF NOT EXISTS s1;
CREATE SCHEMA IF NOT EXISTS s2;
CREATE SCHEMA IF NOT EXISTS s3;
CREATE SCHEMA IF NOT EXISTS s4;

-- s1 = Paris
DROP TABLE IF EXISTS s1.population;
CREATE TABLE s1.population (
    id_personne TEXT,
    nom TEXT,
    prenom TEXT,
    adresse TEXT,
    csp TEXT
);

DROP TABLE IF EXISTS s1.consommation;
CREATE TABLE s1.consommation (
    id_adr TEXT,
    n TEXT,
    nom_rue TEXT,
    code_postal TEXT,
    nb_kw_jour NUMERIC
);

-- s2 = Evry
DROP TABLE IF EXISTS s2.population;
CREATE TABLE s2.population (
    id_personne TEXT,
    nom TEXT,
    prenom TEXT,
    adresse TEXT,
    csp TEXT
);

DROP TABLE IF EXISTS s2.consommation;
CREATE TABLE s2.consommation (
    id_adr TEXT,
    n TEXT,
    nom_rue TEXT,
    code_postal TEXT,
    nb_kw_jour NUMERIC
);

-- s3 = CSP ("Desc" dans le CSV, mot réservé en SQL : renommé description)
DROP TABLE IF EXISTS s3.csp;
CREATE TABLE s3.csp (
    id_csp TEXT,
    description TEXT,
    salaire_moyen NUMERIC,
    salaire_min NUMERIC,
    salaire_max NUMERIC
);

-- s4 = IRIS
DROP TABLE IF EXISTS s4.iris;
CREATE TABLE s4.iris (
    id_rue TEXT,
    id_ville TEXT,
    id_iris TEXT
);
