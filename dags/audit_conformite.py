from datetime import datetime

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


@dag(
    dag_id="audit_conformite",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/dags/sql",
    tags=["audit", "conformite"],
)
def audit_conformite():
    SQLExecuteQueryOperator(
        task_id="taux_conformite_cp",
        conn_id="postgres_projet",
        sql="audit/conformite_cp.sql",
        show_return_value_in_logs=True,
    )

    SQLExecuteQueryOperator(
        task_id="taux_conformite_adresse",
        conn_id="postgres_projet",
        sql="audit/conformite_adresse.sql",
        show_return_value_in_logs=True,
    )


audit_conformite()
