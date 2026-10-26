from datetime import datetime

from airflow.sdk import dag
from airflow.providers.standard.operators.trigger_dagrun import (
    TriggerDagRunOperator,
)
from airflow.providers.common.sql.operators.sql import (
    SQLExecuteQueryOperator,
)


@dag(
    dag_id="pipeline_qualite_global",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/dags/sql",
    tags=[
        "qualite",
        "global"
    ],
)
def pipeline_qualite_global():

    # ========================================================
    # 1. CHARGEMENT DES SOURCES
    # ========================================================

    charger_sources = TriggerDagRunOperator(
        task_id="charger_sources",
        trigger_dag_id="chargement_sources",
        wait_for_completion=True,
        poke_interval=5,
        deferrable=True,
    )

    # ========================================================
    # 2. CALCUL DES CIBLES
    # ========================================================

    calculer_cibles = TriggerDagRunOperator(
        task_id="calculer_cibles",
        trigger_dag_id="calcul_cibles",
        wait_for_completion=True,
        poke_interval=5,
        deferrable=True,
    )

    # ========================================================
    # 3. PREPARATION DE L'HISTORIQUE
    # ========================================================

    initialiser_historique = TriggerDagRunOperator(
        task_id="initialiser_historique",
        trigger_dag_id="creation_historique_qualite",
        wait_for_completion=True,
        poke_interval=5,
        deferrable=True,
    )

    # ========================================================
    # 4. AUDIT COMPLETUDE
    # ========================================================

    auditer_completude = TriggerDagRunOperator(
        task_id="auditer_completude",
        trigger_dag_id="audit_completude",
        wait_for_completion=True,
        poke_interval=5,
        deferrable=True,
    )

    # ========================================================
    # 5. AUDIT CONFORMITE
    # ========================================================

    auditer_conformite = TriggerDagRunOperator(
        task_id="auditer_conformite",
        trigger_dag_id="audit_conformite",
        wait_for_completion=True,
        poke_interval=5,
        deferrable=True,
    )

    # ========================================================
    # 6. AUDIT DOUBLONS
    # ========================================================

    auditer_doublons = TriggerDagRunOperator(
        task_id="auditer_doublons",
        trigger_dag_id="audit_doublons",
        wait_for_completion=True,
        poke_interval=5,
        deferrable=True,
    )

    # ========================================================
    # 7. AUDIT HETEROGENEITE
    # ========================================================

    auditer_heterogeneite = TriggerDagRunOperator(
        task_id="auditer_heterogeneite",
        trigger_dag_id="audit_heterogeneite",
        wait_for_completion=True,
        poke_interval=5,
        deferrable=True,
    )

    # ========================================================
    # 8. CONSULTATION FINALE DE L'HISTORIQUE
    # ========================================================

    consulter_historique = SQLExecuteQueryOperator(
        task_id="consulter_historique_global",
        conn_id="postgres_projet",
        sql="qualite/consulter_historique_qualite.sql",
        show_return_value_in_logs=True,
    )

    # ========================================================
    # 9. ORCHESTRATION GLOBALE
    # ========================================================

    # Après le chargement :
    # - les cibles peuvent être calculées
    # - l'historique peut être préparé
    charger_sources >> [
        calculer_cibles,
        initialiser_historique
    ]

    # L'historique doit exister avant les audits,
    # car chaque audit va y enregistrer ses mesures.
    initialiser_historique >> [
        auditer_completude,
        auditer_conformite,
        auditer_doublons,
        auditer_heterogeneite
    ]

    # La consultation dépend uniquement des audits
    # qui écrivent réellement dans l'historique.
    [
        auditer_completude,
        auditer_conformite,
        auditer_doublons,
        auditer_heterogeneite
    ] >> consulter_historique


pipeline_qualite_global()