INSERT INTO qualite.historique_qualite
    (
        facteur,
        objet,
        metrique,
        valeur,
        unite
    )
VALUES
    (
        'doublons',
        's1.population <-> s2.population',
        'taux_redondance',
        %(taux_redondance)s,
        '%%'
    ),
    (
        'doublons',
        's1.population <-> s2.population',
        'taux_unicite',
        %(taux_unicite)s,
        '%%'
    );