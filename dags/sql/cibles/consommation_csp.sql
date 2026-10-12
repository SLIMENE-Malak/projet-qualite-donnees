-- Cible : Consommation_CSP (ID_CSP, Conso_moyenne_annuelle, Salaire_Moyen)
-- Population.adresse est écrite "N Nom_Rue, Code_Postal" (avec virgule) : les deux
-- côtés de la jointure sont normalisés (minuscules, virgules et espaces multiples
-- remplacés par un seul espace). L'opérateur || donne NULL si une partie de
-- l'adresse de consommation manque, ce qui exclut la ligne au lieu de la mal joindre.
DROP TABLE IF EXISTS cible.consommation_csp;
CREATE TABLE cible.consommation_csp AS
WITH csp_paris_evry AS (
    SELECT p.csp,
        c.nb_kw_jour
    FROM s1.population p
        JOIN s1.consommation c
            ON regexp_replace(lower(trim(p.adresse)), '[\s,]+', ' ', 'g')
             = regexp_replace(lower(trim(c.n || ' ' || c.nom_rue || ' ' || c.code_postal)), '[\s,]+', ' ', 'g')
    UNION ALL
    SELECT p.csp,
        c.nb_kw_jour
    FROM s2.population p
        JOIN s2.consommation c
            ON regexp_replace(lower(trim(p.adresse)), '[\s,]+', ' ', 'g')
             = regexp_replace(lower(trim(c.n || ' ' || c.nom_rue || ' ' || c.code_postal)), '[\s,]+', ' ', 'g')
)
SELECT s.id_csp,
    avg(pe.nb_kw_jour * 365) AS conso_moyenne_annuelle,
    s.salaire_moyen
FROM csp_paris_evry pe
    JOIN s3.csp s ON s.id_csp = trim(pe.csp)
GROUP BY s.id_csp,
    s.salaire_moyen;
