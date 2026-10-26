SELECT
    id_mesure,

    date_mesure + INTERVAL '1 hour'
        AS date_mesure,

    facteur,
    objet,
    metrique,
    valeur,
    unite

FROM qualite.historique_qualite

ORDER BY
    date_mesure DESC,
    id_mesure DESC;