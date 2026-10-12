from datetime import datetime

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


@dag(
    dag_id="chargement_sources",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/dags/sql",
    tags=["chargement", "sources"],
)
def chargement_sources():
    creation = SQLExecuteQueryOperator(
        task_id="creation_sources",
        conn_id="postgres_projet",
        sql="chargement/creation_sources.sql",
    )

    copie = SQLExecuteQueryOperator(
        task_id="copie_sources",
        conn_id="postgres_projet",
        sql="chargement/copie_sources.sql",
    )

    creation >> copie


chargement_sources()
