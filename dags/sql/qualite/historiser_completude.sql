{% set mesures_population =
    ti.xcom_pull(task_ids='taux_completude_population') %}

{% set mesures_consommation =
    ti.xcom_pull(task_ids='taux_completude_consommation') %}

{% set mesures_csp =
    ti.xcom_pull(task_ids='taux_completude_csp') %}

{% set mesures_iris =
    ti.xcom_pull(task_ids='taux_completude_iris') %}

{% set mesures =
    mesures_population
    + mesures_consommation
    + mesures_csp
    + mesures_iris
%}

INSERT INTO qualite.historique_qualite
(
    facteur,
    objet,
    metrique,
    valeur,
    unite
)
VALUES

{% for mesure in mesures %}

(
    'completude',

    '{{ mesure["table_auditee"] }}.{{ mesure["colonne"] }}',

    'taux_completude',

    {{ mesure["taux_completude"] }},

    '%'
)

{% if not loop.last %},{% endif %}

{% endfor %};