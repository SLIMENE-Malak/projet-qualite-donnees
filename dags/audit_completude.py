from datetime import datetime
from decimal import Decimal
import logging

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


log = logging.getLogger(__name__)


# ============================================================
# AFFICHAGE DES RESULTATS
# ============================================================

COLONNES_AFFICHEES = [
    "table_auditee",
    "colonne",
    "taux_completude"
]


def formater_tableau(colonnes, lignes):
    """
    Met en forme des lignes de résultat SQL
    en tableau texte aligné.
    """

    cellules = [
        [
            "" if valeur is None else str(valeur)
            for valeur in ligne
        ]
        for ligne in lignes
    ]

    largeurs = [
        max(
            [len(nom)]
            + [
                len(ligne[i])
                for ligne in cellules
            ]
        )
        for i, nom in enumerate(colonnes)
    ]

    numerique = [
        any(
            isinstance(
                ligne[i],
                (int, float, Decimal)
            )
            for ligne in lignes
        )
        for i in range(len(colonnes))
    ]

    def formater_ligne(valeurs):

        return " | ".join(
            valeur.rjust(largeur)
            if est_numerique
            else valeur.ljust(largeur)

            for (
                valeur,
                largeur,
                est_numerique
            ) in zip(
                valeurs,
                largeurs,
                numerique
            )
        )

    separateur = "-+-".join(
        "-" * largeur
        for largeur in largeurs
    )

    return "\n".join(
        [
            formater_ligne(colonnes),
            separateur
        ]
        + [
            formater_ligne(ligne)
            for ligne in cellules
        ]
    )


def afficher_resultat(
    results,
    descriptions
):
    """
    Affiche le résultat SQL dans les logs
    et renvoie les mesures dans XCom.
    """

    lignes = results[-1]

    colonnes = [
        description[0]
        for description in descriptions[-1]
    ]

    mesures = [
        dict(
            zip(
                colonnes,
                ligne
            )
        )
        for ligne in lignes
    ]

    affichage = [
        [
            mesure[colonne]
            for colonne in COLONNES_AFFICHEES
        ]
        for mesure in mesures
    ]

    log.info(
        "Résultat :\n%s",
        formater_tableau(
            COLONNES_AFFICHEES,
            affichage
        )
    )

    return [mesures]


# ============================================================
# DAG
# ============================================================

@dag(
    dag_id="audit_completude",
    start_date=datetime(
        2026,
        1,
        1
    ),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/dags/sql",
    tags=[
        "audit",
        "completude"
    ],
)
def audit_completude():

    # ========================================================
    # 1. COMPLETUDE POPULATION
    # ========================================================

    completude_population = SQLExecuteQueryOperator(
        task_id="taux_completude_population",
        conn_id="postgres_projet",
        sql="audit/completude_population.sql",
        output_processor=afficher_resultat,
    )

    # ========================================================
    # 2. COMPLETUDE CONSOMMATION
    # ========================================================

    completude_consommation = SQLExecuteQueryOperator(
        task_id="taux_completude_consommation",
        conn_id="postgres_projet",
        sql="audit/completude_consommation.sql",
        output_processor=afficher_resultat,
    )

    # ========================================================
    # 3. COMPLETUDE CSP
    # ========================================================

    completude_csp = SQLExecuteQueryOperator(
        task_id="taux_completude_csp",
        conn_id="postgres_projet",
        sql="audit/completude_csp.sql",
        output_processor=afficher_resultat,
    )

    # ========================================================
    # 4. COMPLETUDE IRIS
    # ========================================================

    completude_iris = SQLExecuteQueryOperator(
        task_id="taux_completude_iris",
        conn_id="postgres_projet",
        sql="audit/completude_iris.sql",
        output_processor=afficher_resultat,
    )

    # ========================================================
    # 5. HISTORISATION
    # ========================================================

    enregistrer_historique = SQLExecuteQueryOperator(
        task_id="enregistrer_historique_completude",
        conn_id="postgres_projet",
        sql="qualite/historiser_completude.sql",
    )

    # Les quatre audits doivent être terminés
    # avant l'enregistrement de l'historique.

    [
        completude_population,
        completude_consommation,
        completude_csp,
        completude_iris
    ] >> enregistrer_historique


audit_completude()