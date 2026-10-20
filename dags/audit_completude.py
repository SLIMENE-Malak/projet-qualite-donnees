from datetime import datetime
from decimal import Decimal
import logging

from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

log = logging.getLogger(__name__)

# Un fichier SQL par table auditée : dags/sql/audit/completude_<table>.sql
TABLES_AUDITEES = ["population", "consommation", "csp", "iris"]

# Colonnes du résultat affichées dans les logs (XCom garde toutes les colonnes)
COLONNES_AFFICHEES = ["table_auditee", "colonne", "taux_completude"]


def formater_tableau(colonnes, lignes):
    """Met en forme des lignes de résultat SQL en tableau texte aligné."""
    cellules = [["" if v is None else str(v) for v in ligne] for ligne in lignes]
    largeurs = [
        max([len(nom)] + [len(ligne[i]) for ligne in cellules])
        for i, nom in enumerate(colonnes)
    ]
    # Nombres alignés à droite, texte à gauche
    numerique = [
        any(isinstance(ligne[i], (int, float, Decimal)) for ligne in lignes)
        for i in range(len(colonnes))
    ]

    def formater_ligne(valeurs):
        return " | ".join(
            v.rjust(l) if num else v.ljust(l)
            for v, l, num in zip(valeurs, largeurs, numerique)
        )

    separateur = "-+-".join("-" * l for l in largeurs)
    return "\n".join(
        [formater_ligne(colonnes), separateur]
        + [formater_ligne(ligne) for ligne in cellules]
    )

 
def afficher_resultat(results, descriptions):
    """Affiche le résultat de la requête en tableau dans les logs et le renvoie en XCom."""
    lignes = results[-1]
    colonnes = [description[0] for description in descriptions[-1]]
    mesures = [dict(zip(colonnes, ligne)) for ligne in lignes]

    affichage = [[mesure[c] for c in COLONNES_AFFICHEES] for mesure in mesures]
    log.info("Résultat :\n%s", formater_tableau(COLONNES_AFFICHEES, affichage))
    return mesures


@dag(
    dag_id="audit_completude",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/dags/sql",
    tags=["audit", "completude"],
)
def audit_completude():
    for table in TABLES_AUDITEES:
        SQLExecuteQueryOperator(
            task_id=f"taux_completude_{table}",
            conn_id="postgres_projet",
            sql=f"audit/completude_{table}.sql",
            output_processor=afficher_resultat,
        )


audit_completude()
