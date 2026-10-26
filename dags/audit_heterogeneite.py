from datetime import datetime

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


# ============================================================
# PREPARATION DU RESULTAT POUR XCOM
# ============================================================

def preparer_mesures(results, descriptions):
    """
    Transforme le résultat SQL en dictionnaire
    afin de pouvoir l'utiliser pour l'historisation.
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

    return [mesures]


# ============================================================
# DAG
# ============================================================

@dag(
    dag_id="audit_heterogeneite",
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
        "heterogeneite"
    ],
)
def audit_heterogeneite():

    # ========================================================
    # 1. CALCUL DU RATIO D'ECHELLE
    # ========================================================

    ratio_echelle = SQLExecuteQueryOperator(
        task_id="ratio_echelle_consommation",
        conn_id="postgres_projet",
        sql="audit/heterogeneite_echelle.sql",
        output_processor=preparer_mesures,
        show_return_value_in_logs=True,
    )

    # ========================================================
    # 2. HISTORISATION
    # ========================================================

    enregistrer_historique = SQLExecuteQueryOperator(
        task_id="enregistrer_historique_heterogeneite",
        conn_id="postgres_projet",
        sql="qualite/historiser_heterogeneite.sql",
    )

    ratio_echelle >> enregistrer_historique


audit_heterogeneite()