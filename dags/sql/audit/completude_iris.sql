WITH comptes AS (
    SELECT 's4.iris' AS table_auditee,
        COUNT(*) AS nb_lignes,
        COUNT(id_rue) AS id_rue,
        COUNT(id_ville) AS id_ville,
        COUNT(id_iris) AS id_iris
    FROM s4.iris
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
        VALUES ('id_rue', c.id_rue),
            ('id_ville', c.id_ville),
            ('id_iris', c.id_iris)
    ) AS v(colonne, nb_non_null)
ORDER BY c.table_auditee,
    v.colonne;
