SELECT 'S1' AS source,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE TRIM(Adresse) ~* '^[0-9]+( ?(bis|ter))? [^,]*[[:alpha:]][^,]*,? 75[0-9]{3}$'
        ) / NULLIF(COUNT(Adresse), 0),
        2
    ) AS taux_conformite_adresse
FROM S1.Population
UNION ALL
SELECT 'S2',
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE TRIM(Adresse) ~* '^[0-9]+( ?(bis|ter))? [^,]*[[:alpha:]][^,]*,? 91[0-9]{3}$'
        ) / NULLIF(COUNT(Adresse), 0),
        2
    )
FROM S2.Population;