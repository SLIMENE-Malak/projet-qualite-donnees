{% set mesures_cp =
    ti.xcom_pull(task_ids='taux_conformite_cp') %}

{% set mesures_adresse =
    ti.xcom_pull(task_ids='taux_conformite_adresse') %}


INSERT INTO qualite.historique_qualite
(
    facteur,
    objet,
    metrique,
    valeur,
    unite
)
VALUES

{% for mesure in mesures_cp %}

(
    'conformite',

    '{% if mesure["source"] == "S1" %}s1.consommation.code_postal{% else %}s2.consommation.code_postal{% endif %}',

    'taux_conformite_cp',

    {{ mesure["taux_conformite_cp"] }},

    '%'
),

{% endfor %}


{% for mesure in mesures_adresse %}

(
    'conformite',

    '{% if mesure["source"] == "S1" %}s1.population.adresse{% else %}s2.population.adresse{% endif %}',

    'taux_conformite_adresse',

    {{ mesure["taux_conformite_adresse"] }},

    '%'
)

{% if not loop.last %},{% endif %}

{% endfor %};