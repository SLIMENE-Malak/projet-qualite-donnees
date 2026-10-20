WITH comptes AS (
    SELECT 's3.csp' AS table_auditee,
        COUNT(*) AS nb_lignes,
        COUNT(id_csp) AS id_csp,
        COUNT(salaire_moyen) AS salaire_moyen
    FROM s3.csp
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
        VALUES ('id_csp', c.id_csp),
            ('salaire_moyen', c.salaire_moyen)
    ) AS v(colonne, nb_non_null)
ORDER BY c.table_auditee,
    v.colonne;
