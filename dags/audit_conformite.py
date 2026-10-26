from datetime import datetime

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


# ============================================================
# CONVERSION DU RESULTAT SQL EN MESURES POUR XCOM
# ============================================================

def preparer_mesures(results, descriptions):
    """
    Transforme les lignes SQL en dictionnaires afin
    qu'elles puissent être réutilisées par la tâche
    d'historisation.
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
    dag_id="audit_conformite",
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
        "conformite"
    ],
)
def audit_conformite():

    # ========================================================
    # 1. CONFORMITE DES CODES POSTAUX
    # ========================================================

    conformite_cp = SQLExecuteQueryOperator(
        task_id="taux_conformite_cp",
        conn_id="postgres_projet",
        sql="audit/conformite_cp.sql",
        output_processor=preparer_mesures,
        show_return_value_in_logs=True,
    )

    # ========================================================
    # 2. CONFORMITE DES ADRESSES
    # ========================================================

    conformite_adresse = SQLExecuteQueryOperator(
        task_id="taux_conformite_adresse",
        conn_id="postgres_projet",
        sql="audit/conformite_adresse.sql",
        output_processor=preparer_mesures,
        show_return_value_in_logs=True,
    )

    # ========================================================
    # 3. HISTORISATION
    # ========================================================

    enregistrer_historique = SQLExecuteQueryOperator(
        task_id="enregistrer_historique_conformite",
        conn_id="postgres_projet",
        sql="qualite/historiser_conformite.sql",
    )

    [
        conformite_cp,
        conformite_adresse
    ] >> enregistrer_historique


audit_conformite()