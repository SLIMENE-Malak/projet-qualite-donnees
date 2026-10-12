-- Copie des CSV de data/ dans les tables sources.
-- COPY côté serveur : les fichiers sont lus dans le conteneur postgres-projet,
-- où data/ est monté sur /data. Les colonnes sont listées explicitement :
-- l'en-tête du CSV est ignoré, seule la position compte.
-- Une cellule vide non entourée de guillemets est chargée comme NULL.
TRUNCATE s1.population, s1.consommation, s2.population, s2.consommation, s3.csp, s4.iris;

COPY s1.population (id_personne, nom, prenom, adresse, csp)
FROM '/data/population_paris.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY s1.consommation (id_adr, n, nom_rue, code_postal, nb_kw_jour)
FROM '/data/consommation_paris.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY s2.population (id_personne, nom, prenom, adresse, csp)
FROM '/data/population_evry.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY s2.consommation (id_adr, n, nom_rue, code_postal, nb_kw_jour)
FROM '/data/consommation_evry.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY s3.csp (id_csp, description, salaire_moyen, salaire_min, salaire_max)
FROM '/data/csp_reference.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY s4.iris (id_rue, id_ville, id_iris)
FROM '/data/iris_reference.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
