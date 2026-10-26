from datetime import datetime

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


@dag(
    dag_id="creation_historique_qualite",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/dags/sql",
    tags=["qualite", "historique"],
)
def creation_historique_qualite():

    # ========================================================
    # 1. CREATION DU METAMODELE
    # ========================================================

    creer_historique = SQLExecuteQueryOperator(
        task_id="creer_historique_qualite",
        conn_id="postgres_projet",
        sql="qualite/creation_historique_qualite.sql",
    )

    # ========================================================
    # 2. VERIFICATION DU NOMBRE DE MESURES
    # ========================================================

    verifier_historique = SQLExecuteQueryOperator(
        task_id="verifier_historique_qualite",
        conn_id="postgres_projet",
        sql="qualite/verifier_historique_qualite.sql",
        show_return_value_in_logs=True,
    )

    # ========================================================
    # 3. CONSULTATION DE L'HISTORIQUE
    # ========================================================

    consulter_historique = SQLExecuteQueryOperator(
        task_id="consulter_historique_qualite",
        conn_id="postgres_projet",
        sql="qualite/consulter_historique_qualite.sql",
        show_return_value_in_logs=True,
    )

    # ========================================================
    # ORDRE D'EXECUTION
    # ========================================================

    (
        creer_historique
        >> verifier_historique
        >> consulter_historique
    )


creation_historique_qualite()