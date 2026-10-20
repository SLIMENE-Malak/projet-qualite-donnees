WITH comptes AS (
    SELECT 's1.consommation' AS table_auditee,
        COUNT(*) AS nb_lignes,
        COUNT(n) AS n,
        COUNT(nom_rue) AS nom_rue,
        COUNT(code_postal) AS code_postal,
        COUNT(nb_kw_jour) AS nb_kw_jour
    FROM s1.consommation
    UNION ALL
    SELECT 's2.consommation',
        COUNT(*),
        COUNT(n),
        COUNT(nom_rue),
        COUNT(code_postal),
        COUNT(nb_kw_jour)
    FROM s2.consommation
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
        VALUES ('n', c.n),
            ('nom_rue', c.nom_rue),
            ('code_postal', c.code_postal),
            ('nb_kw_jour', c.nb_kw_jour)
    ) AS v(colonne, nb_non_null)
ORDER BY c.table_auditee,
    v.colonne;
