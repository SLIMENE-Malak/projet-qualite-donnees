WITH comptes AS (
    SELECT 's1.population' AS table_auditee,
        COUNT(*) AS nb_lignes,
        COUNT(adresse) AS adresse,
        COUNT(csp) AS csp
    FROM s1.population
    UNION ALL
    SELECT 's2.population',
        COUNT(*),
        COUNT(adresse),
        COUNT(csp)
    FROM s2.population
)
SELECT c.table_auditee,
    v.colonne,
    v.nb_non_null AS numerateur,
    c.nb_lignes AS denominateur,
    ROUND(
        100.0 * v.nb_non_null / NULLIF(c.nb_lignes, 0),
        2
    ) AS taux_completude
FROM comptes AS c
    CROSS JOIN LATERAL (
        VALUES ('adresse', c.adresse),
            ('csp', c.csp)
    ) AS v(colonne, nb_non_null)
ORDER BY c.table_auditee,
    v.colonne;