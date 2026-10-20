-- Cible : Consommation_CSP (ID_CSP, Conso_moyenne_annuelle, Salaire_Moyen)
-- Paris et Evry sont calculés séparément puis réunis, car leurs formats diffèrent :
--   * adresse Paris "Paris, 20 rue Arthur Groussier", Evry "Evry-Courcouronnes, 91000, 19 Boulevard Aguado" ;
--   * CSP Paris = libellé ("Cadre", "Commerçant / Artisan"), CSP Evry = id_csp.
-- Normalisation : minuscules, sans espaces en bord. Les accents ne sont retirés (translate)
-- que dans population.adresse ("Allée") : nom_rue est déjà en majuscules sans accent ("ALLEE").
-- Jointure adresse : on extrait de population.adresse le numéro (bis/ter compris) et la
-- fin de l'adresse ; le numéro doit égaler n et la rue doit finir par nom_rue (le type
-- de voie, absent de nom_rue à Paris, est ainsi ignoré). "2bis" ne joint pas "2".
-- Jointure CSP Paris : par la table de correspondance s3.correspondance_csp. Un libellé
-- sans id_csp (Etudiant, Retraitée) ou absent de la table sort du calcul.
-- Les lignes sont réunies avant la moyenne : pas de moyenne de moyennes.
DROP TABLE IF EXISTS cible.consommation_csp;
CREATE TABLE cible.consommation_csp AS
WITH population_paris AS (
    SELECT trim(csp) AS csp,
        regexp_match(
            translate(lower(trim(adresse)), 'àâäáéèêëíîïóôöúùûüÿç', 'aaaaeeeeiiiooouuuuyc'),
            '(\d+(?:\s?(?:bis|ter))?)\s+([^0-9,]+)$'
        ) AS adr
    FROM s1.population
),
population_evry AS (
    SELECT trim(csp) AS csp,
        regexp_match(
            translate(lower(trim(adresse)), 'àâäáéèêëíîïóôöúùûüÿç', 'aaaaeeeeiiiooouuuuyc'),
            '(\d+(?:\s?(?:bis|ter))?)\s+([^0-9,]+)$'
        ) AS adr
    FROM s2.population
),
consommation_paris AS (
    SELECT lower(trim(n)) AS n,
        lower(trim(nom_rue)) AS rue,
        nb_kw_jour
    FROM s1.consommation
),
consommation_evry AS (
    SELECT lower(trim(n)) AS n,
        lower(trim(nom_rue)) AS rue,
        nb_kw_jour
    FROM s2.consommation
),
consommation_csp_paris AS (
    SELECT m.id_csp,
        c.nb_kw_jour
    FROM population_paris p
        JOIN consommation_paris c
            ON replace(p.adr[1], ' ', '') = c.n
            AND right(' ' || trim(p.adr[2]), length(c.rue) + 1) = ' ' || c.rue
        JOIN s3.correspondance_csp m ON m.libelle_source = p.csp
),
consommation_csp_evry AS (
    SELECT p.csp AS id_csp,
        c.nb_kw_jour
    FROM population_evry p
        JOIN consommation_evry c
            ON replace(p.adr[1], ' ', '') = c.n
            AND right(' ' || trim(p.adr[2]), length(c.rue) + 1) = ' ' || c.rue
),
consommation_csp_paris_evry AS (
    SELECT id_csp, nb_kw_jour FROM consommation_csp_paris
    UNION ALL
    SELECT id_csp, nb_kw_jour FROM consommation_csp_evry
)
SELECT s.id_csp,
    avg(pe.nb_kw_jour * 365) AS conso_moyenne_annuelle,
    s.salaire_moyen
FROM consommation_csp_paris_evry pe
    JOIN s3.csp s ON s.id_csp = pe.id_csp
GROUP BY s.id_csp,
    s.salaire_moyen;
ALTER TABLE cible.consommation_csp ADD PRIMARY KEY (id_csp);
