-- Table de correspondance (transcodage) : libellé CSP de s1.population -> s3.csp.id_csp.
-- Population Paris écrit la CSP en libellé ("Cadre"), Population Evry en id_csp ("3").
-- Les sources ne sont jamais modifiées : la traduction se fait par jointure sur cette table.
-- libelle_source reprend la valeur exacte de la source ; une nouvelle écriture absente
-- d'ici ne sera pas rattachée et ressortira dans l'audit, au lieu d'être devinée.
-- id_csp NULL : libellé connu, sans catégorie dans s3.csp (référentiel limité aux CSP 1 à 6).
DROP TABLE IF EXISTS s3.correspondance_csp;
CREATE TABLE s3.correspondance_csp (
    libelle_source TEXT PRIMARY KEY,
    id_csp TEXT
);
INSERT INTO s3.correspondance_csp (libelle_source, id_csp)
VALUES ('Agriculteur', '1'),
    ('Commerçant / Artisan', '2'),
    ('Cadre', '3'),
    ('cadres et professions intellectuelles supérieures', '3'),
    ('Professions intermédiaires', '4'),
    ('Employé', '5'),
    ('Ouvrier', '6'),
    ('Etudiant', NULL),
    ('Retraitée', NULL);
