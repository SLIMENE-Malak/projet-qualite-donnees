from datetime import datetime

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


@dag(
    dag_id="calcul_cibles",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/dags/sql",
    tags=["cibles", "mapping"],
)
def calcul_cibles():
    SQLExecuteQueryOperator(
        task_id="calcul_consommation_iris_paris",
        conn_id="postgres_projet",
        sql="cibles/consommation_iris_paris.sql",
    )

    SQLExecuteQueryOperator(
        task_id="calcul_consommation_iris_evry",
        conn_id="postgres_projet",
        sql="cibles/consommation_iris_evry.sql",
    )

    SQLExecuteQueryOperator(
        task_id="calcul_consommation_csp",
        conn_id="postgres_projet",
        sql="cibles/consommation_csp.sql",
    )


calcul_cibles()