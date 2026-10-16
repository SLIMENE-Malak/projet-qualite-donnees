from datetime import datetime
import logging
import re
import unicodedata

import pandas as pd

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook


# ============================================================
# PARAMETRES
# ============================================================

SEUIL_DOUBLON = 0.80

MODELE_ADRESSE = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# ============================================================
# 1. NORMALISATION
# ============================================================

def normaliser_texte(valeur):
    """
    Normalise une valeur textuelle afin de faciliter
    la comparaison entre deux enregistrements.
    """

    # Valeur manquante
    if pd.isna(valeur):
        return ""

    # Conversion en texte + minuscules
    texte = str(valeur).lower()

    # Suppression des accents
    texte = unicodedata.normalize(
        "NFKD",
        texte
    )

    texte = "".join(
        caractere
        for caractere in texte
        if not unicodedata.combining(caractere)
    )

    # Suppression de la ponctuation
    texte = re.sub(
        r"[^a-z0-9\s]",
        " ",
        texte
    )

    # Suppression des espaces multiples
    texte = re.sub(
        r"\s+",
        " ",
        texte
    ).strip()

    return texte


# ============================================================
# 2. DISTANCE DE LEVENSHTEIN
# ============================================================

def distance_levenshtein(texte1, texte2):
    """
    Calcule la distance de Levenshtein entre deux chaînes.
    """

    if texte1 == texte2:
        return 0

    if len(texte1) == 0:
        return len(texte2)

    if len(texte2) == 0:
        return len(texte1)

    ligne_precedente = list(
        range(len(texte2) + 1)
    )

    for i, caractere1 in enumerate(
        texte1,
        start=1
    ):

        ligne_courante = [i]

        for j, caractere2 in enumerate(
            texte2,
            start=1
        ):

            cout = (
                0
                if caractere1 == caractere2
                else 1
            )

            insertion = (
                ligne_courante[j - 1] + 1
            )

            suppression = (
                ligne_precedente[j] + 1
            )

            substitution = (
                ligne_precedente[j - 1]
                + cout
            )

            ligne_courante.append(
                min(
                    insertion,
                    suppression,
                    substitution
                )
            )

        ligne_precedente = ligne_courante

    return ligne_precedente[-1]


# ============================================================
# 3. SIMILARITE LEVENSHTEIN
# ============================================================

def similarite_levenshtein(texte1, texte2):
    """
    Transforme la distance de Levenshtein
    en score de similarité compris entre 0 et 1.
    """

    if not texte1 or not texte2:
        return 0.0

    distance = distance_levenshtein(
        texte1,
        texte2
    )

    longueur_max = max(
        len(texte1),
        len(texte2)
    )

    similarite = (
        1
        - distance / longueur_max
    )

    return similarite


# ============================================================
# 4. DAG AIRFLOW
# ============================================================

@dag(
    dag_id="audit_doublons",
    start_date=datetime(
        2026,
        1,
        1
    ),
    schedule=None,
    catchup=False,
    tags=[
        "audit",
        "doublons"
    ],
)
def audit_doublons():

    @task
    def calculer_similarites():

        # Import dans la tâche pour éviter
        # les problèmes lors du parsing du DAG
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity

        # ====================================================
        # 5. CHARGEMENT DES DONNEES
        # ====================================================

        hook = PostgresHook(
            postgres_conn_id="postgres_projet"
        )

        population_paris = (
            hook.get_df(
                """
                SELECT *
                FROM s1.population;
                """
            )
            .reset_index(drop=True)
        )

        population_evry = (
            hook.get_df(
                """
                SELECT *
                FROM s2.population;
                """
            )
            .reset_index(drop=True)
        )

        nombre_paris = len(
            population_paris
        )

        nombre_evry = len(
            population_evry
        )

        logging.info(
            "Nombre de personnes Paris : %s",
            nombre_paris
        )

        logging.info(
            "Nombre de personnes Evry : %s",
            nombre_evry
        )

        # ====================================================
        # 6. NORMALISATION
        # ====================================================

        colonnes_comparaison = [
            "nom",
            "prenom",
            "adresse"
        ]

        for colonne in colonnes_comparaison:

            population_paris[
                colonne + "_norm"
            ] = population_paris[
                colonne
            ].apply(
                normaliser_texte
            )

            population_evry[
                colonne + "_norm"
            ] = population_evry[
                colonne
            ].apply(
                normaliser_texte
            )

        logging.info(
            "Normalisation terminée."
        )

        # ====================================================
        # 7. MODELE DE REPRESENTATION VECTORIELLE
        # ====================================================

        logging.info(
            "Chargement du modèle "
            "de représentation vectorielle..."
        )

        modele = SentenceTransformer(
            MODELE_ADRESSE,
            local_files_only=True
        )

        logging.info(
            "Modèle chargé avec succès."
        )

        # ====================================================
        # 8. VECTEURS DES ADRESSES
        # ====================================================

        adresses_paris = (
            population_paris[
                "adresse_norm"
            ]
            .fillna("")
            .tolist()
        )

        adresses_evry = (
            population_evry[
                "adresse_norm"
            ]
            .fillna("")
            .tolist()
        )

        logging.info(
            "Création des vecteurs des adresses..."
        )

        vecteurs_paris = modele.encode(
            adresses_paris,
            show_progress_bar=False
        )

        vecteurs_evry = modele.encode(
            adresses_evry,
            show_progress_bar=False
        )

        # Similarités cosinus de toutes
        # les adresses Paris × Evry
        matrice_cosinus = cosine_similarity(
            vecteurs_paris,
            vecteurs_evry
        )

        logging.info(
            "Similarités vectorielles "
            "des adresses calculées."
        )

        # ====================================================
        # 9. COMPARAISON DES PAIRES
        # ====================================================

        comparaisons = []

        for (
            index_paris,
            paris
        ) in population_paris.iterrows():

            for (
                index_evry,
                evry
            ) in population_evry.iterrows():

                # --------------------------------------------
                # NOM : Levenshtein
                # --------------------------------------------

                sim_nom = (
                    similarite_levenshtein(
                        paris["nom_norm"],
                        evry["nom_norm"]
                    )
                )

                # --------------------------------------------
                # PRENOM : Levenshtein
                # --------------------------------------------

                sim_prenom = (
                    similarite_levenshtein(
                        paris["prenom_norm"],
                        evry["prenom_norm"]
                    )
                )

                # --------------------------------------------
                # ADRESSE : Levenshtein
                # --------------------------------------------

                sim_adresse_lev = (
                    similarite_levenshtein(
                        paris["adresse_norm"],
                        evry["adresse_norm"]
                    )
                )

                # --------------------------------------------
                # ADRESSE : représentation vectorielle
                # + similarité cosinus
                # --------------------------------------------

                if (
                    paris["adresse_norm"]
                    and evry["adresse_norm"]
                ):

                    sim_adresse_sem = float(
                        matrice_cosinus[
                            index_paris,
                            index_evry
                        ]
                    )

                    # Score limité à l'intervalle [0, 1]
                    sim_adresse_sem = max(
                        0.0,
                        min(
                            1.0,
                            sim_adresse_sem
                        )
                    )

                else:

                    sim_adresse_sem = 0.0

                # --------------------------------------------
                # SCORE ADRESSE
                # --------------------------------------------

                score_adresse = (
                    sim_adresse_lev
                    + sim_adresse_sem
                ) / 2

                # --------------------------------------------
                # SCORE GLOBAL
                # --------------------------------------------

                score_global = (
                    sim_nom
                    + sim_prenom
                    + score_adresse
                ) / 3

                # --------------------------------------------
                # STOCKAGE
                # --------------------------------------------

                comparaisons.append(
                    {
                        "id_paris":
                            paris["id_personne"],

                        "id_evry":
                            evry["id_personne"],

                        "nom_paris":
                            paris["nom"],

                        "nom_evry":
                            evry["nom"],

                        "prenom_paris":
                            paris["prenom"],

                        "prenom_evry":
                            evry["prenom"],

                        "adresse_paris":
                            paris["adresse"],

                        "adresse_evry":
                            evry["adresse"],

                        "sim_nom":
                            sim_nom,

                        "sim_prenom":
                            sim_prenom,

                        "sim_adresse_lev":
                            sim_adresse_lev,

                        "sim_adresse_sem":
                            sim_adresse_sem,

                        "score_adresse":
                            score_adresse,

                        "score_global":
                            score_global,
                    }
                )

        # ====================================================
        # 10. TABLEAU DES RESULTATS
        # ====================================================

        resultats = pd.DataFrame(
            comparaisons
        )

        resultats = (
            resultats
            .sort_values(
                by="score_global",
                ascending=False
            )
            .reset_index(drop=True)
        )

        logging.info(
            "Nombre total de comparaisons : %s",
            len(resultats)
        )

        # ====================================================
        # 11. ANALYSE DES SEUILS
        # ====================================================

        seuils_testes = [
            0.70,
            0.75,
            0.80,
            0.85,
            0.90
        ]

        logging.info(
            "========== ANALYSE DES SEUILS =========="
        )

        for seuil in seuils_testes:

            nombre_paires = (
                resultats[
                    "score_global"
                ] >= seuil
            ).sum()

            pourcentage = (
                nombre_paires
                / len(resultats)
            ) * 100

            logging.info(
                "Seuil %.2f : %s paires "
                "(%.2f %%)",
                seuil,
                nombre_paires,
                pourcentage
            )

        # ====================================================
        # 12. MEILLEUR MATCH POUR CHAQUE PERSONNE DE PARIS
        # ====================================================

        index_meilleur_paris = (
            resultats
            .groupby(
                "id_paris"
            )["score_global"]
            .idxmax()
        )

        meilleurs_pour_paris = (
            resultats
            .loc[
                index_meilleur_paris
            ]
            .copy()
        )

        # ====================================================
        # 13. MEILLEUR MATCH POUR CHAQUE PERSONNE D'EVRY
        # ====================================================

        index_meilleur_evry = (
            resultats
            .groupby(
                "id_evry"
            )["score_global"]
            .idxmax()
        )

        meilleurs_pour_evry = (
            resultats
            .loc[
                index_meilleur_evry,
                [
                    "id_paris",
                    "id_evry"
                ]
            ]
            .copy()
        )

        # ====================================================
        # 14. CORRESPONDANCES MUTUELLES
        # ====================================================

        # Une paire est retenue uniquement si :
        #
        # Paris considère Evry comme son meilleur match
        # ET
        # Evry considère Paris comme son meilleur match.

        correspondances_mutuelles = (
            meilleurs_pour_paris
            .merge(
                meilleurs_pour_evry,
                on=[
                    "id_paris",
                    "id_evry"
                ],
                how="inner"
            )
        )

        logging.info(
            "Nombre de correspondances mutuelles : %s",
            len(correspondances_mutuelles)
        )

        # ====================================================
        # 15. APPLICATION DU SEUIL FINAL
        # ====================================================

        doublons_retenus = (
            correspondances_mutuelles[
                correspondances_mutuelles[
                    "score_global"
                ] >= SEUIL_DOUBLON
            ]
            .copy()
        )

        doublons_retenus = (
            doublons_retenus
            .sort_values(
                by="score_global",
                ascending=False
            )
            .reset_index(drop=True)
        )

        nombre_paires_doublons = len(
            doublons_retenus
        )

        # ====================================================
        # 16. CALCUL DES METRIQUES
        # ====================================================

        nombre_total_enregistrements = (
            nombre_paris
            + nombre_evry
        )

        # ----------------------------------------------------
        # ENREGISTREMENTS CONCERNES PAR UN DOUBLON
        # ----------------------------------------------------

        # Une paire contient deux enregistrements :
        # un de Paris et un d'Evry.
        nombre_enregistrements_concernes = (
            nombre_paires_doublons * 2
        )

        taux_enregistrements_concernes = (
            nombre_enregistrements_concernes
            / nombre_total_enregistrements
        ) * 100

        # ----------------------------------------------------
        # ENREGISTREMENTS REDONDANTS
        # ----------------------------------------------------

        # Dans une paire de doublons,
        # une seule ligne est réellement en trop.
        nombre_enregistrements_redondants = (
            nombre_paires_doublons
        )

        taux_redondance = (
            nombre_enregistrements_redondants
            / nombre_total_enregistrements
        ) * 100

        # ----------------------------------------------------
        # TAUX D'UNICITE
        # ----------------------------------------------------

        nombre_entites_uniques = (
            nombre_total_enregistrements
            - nombre_enregistrements_redondants
        )

        taux_unicite = (
            nombre_entites_uniques
            / nombre_total_enregistrements
        ) * 100

        # ----------------------------------------------------
        # CORRESPONDANCE INTER-SOURCES
        # ----------------------------------------------------

        taux_correspondance_inter_sources = (
            nombre_paires_doublons
            / min(
                nombre_paris,
                nombre_evry
            )
        ) * 100

        # ====================================================
        # 17. AFFICHAGE DES DOUBLONS
        # ====================================================

        affichage_doublons = (
            doublons_retenus.copy()
        )

        colonnes_scores = [
            "sim_nom",
            "sim_prenom",
            "sim_adresse_lev",
            "sim_adresse_sem",
            "score_adresse",
            "score_global"
        ]

        if not affichage_doublons.empty:

            affichage_doublons[
                colonnes_scores
            ] = (
                affichage_doublons[
                    colonnes_scores
                ]
                .round(4)
            )

        logging.info(
            "========== DOUBLONS RETENUS =========="
        )

        logging.info(
            "Seuil final : %.2f",
            SEUIL_DOUBLON
        )

        logging.info(
            "Nombre de paires de doublons : %s",
            nombre_paires_doublons
        )

        if not affichage_doublons.empty:

            logging.info(
                "\n%s",
                affichage_doublons[
                    [
                        "id_paris",
                        "id_evry",
                        "nom_paris",
                        "nom_evry",
                        "prenom_paris",
                        "prenom_evry",
                        "adresse_paris",
                        "adresse_evry",
                        "sim_nom",
                        "sim_prenom",
                        "sim_adresse_lev",
                        "sim_adresse_sem",
                        "score_adresse",
                        "score_global"
                    ]
                ].to_string(
                    index=False
                )
            )

        else:

            logging.info(
                "Aucun doublon détecté."
            )

        # ====================================================
        # 18. RESULTAT FINAL DE LA METRIQUE
        # ====================================================

        logging.info(
            "========== METRIQUES DE QUALITE =========="
        )

        logging.info(
            "Nombre total d'enregistrements : %s",
            nombre_total_enregistrements
        )

        logging.info(
            "Nombre de paires de doublons : %s",
            nombre_paires_doublons
        )

        logging.info(
            "Nombre d'enregistrements concernés "
            "par un doublon : %s",
            nombre_enregistrements_concernes
        )

        logging.info(
            "Taux d'enregistrements concernés "
            "par un doublon : %.2f %%",
            taux_enregistrements_concernes
        )

        logging.info(
            "Nombre d'enregistrements "
            "redondants : %s",
            nombre_enregistrements_redondants
        )

        logging.info(
            "Taux de redondance : %.2f %%",
            taux_redondance
        )

        logging.info(
            "Nombre d'entités uniques "
            "après déduplication : %s",
            nombre_entites_uniques
        )

        logging.info(
            "Taux d'unicité : %.2f %%",
            taux_unicite
        )

        logging.info(
            "Taux de correspondance "
            "inter-sources : %.2f %%",
            taux_correspondance_inter_sources
        )

        logging.info(
            "Audit des doublons terminé avec succès."
        )

    calculer_similarites()


audit_doublons()