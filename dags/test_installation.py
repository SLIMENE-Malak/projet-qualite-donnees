from datetime import datetime
from airflow.sdk import dag, task

@dag(start_date=datetime(2026, 1, 1), schedule=None, catchup=False)
def test_installation():

    @task
    def dire_bonjour():
        print("Airflow fonctionne !")

    dire_bonjour()

test_installation()