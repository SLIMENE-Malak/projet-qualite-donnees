{% set mesures =
    ti.xcom_pull(task_ids='ratio_echelle_consommation') %}

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
    'heterogeneite',
    's1.consommation.nb_kw_jour <-> s2.consommation.nb_kw_jour',
    'ratio_echelle',
    {{ mesures[0]["ratio_echelle"] }},
    'ratio'
);