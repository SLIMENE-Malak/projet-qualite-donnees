SELECT 'S1' AS source,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE TRIM(Code_Postal::text) ~ '^75[0-9]{3}$'
        ) / NULLIF(COUNT(Code_Postal), 0),
        2
    ) AS taux_conformite_cp
FROM S1.Consommation
UNION ALL
SELECT 'S2',
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE TRIM(Code_Postal::text) ~ '^91[0-9]{3}$'
        ) / NULLIF(COUNT(Code_Postal), 0),
        2
    )
FROM S2.Consommation;