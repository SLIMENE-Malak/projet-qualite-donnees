from datetime import datetime
from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

@dag(start_date=datetime(2026, 1, 1), schedule=None, catchup=False)
def test_postgres():

    SQLExecuteQueryOperator(
        task_id="lister_schemas",
        conn_id="postgres_projet",
        sql="SELECT schema_name FROM information_schema.schemata;",
    )

test_postgres()