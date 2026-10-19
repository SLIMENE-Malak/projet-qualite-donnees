from datetime import datetime

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


@dag(
    dag_id="audit_heterogeneite",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/dags/sql",
    tags=["audit", "heterogeneite"],
)
def audit_heterogeneite():
    SQLExecuteQueryOperator(
        task_id="ratio_echelle_consommation",
        conn_id="postgres_projet",
        sql="audit/heterogeneite_echelle.sql",
        show_return_value_in_logs=True,
    )


audit_heterogeneite()
