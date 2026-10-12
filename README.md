# Projet qualité des données de consommation énergétique

Projet M2 DataScale : audit puis nettoyage de données de consommation électrique (Paris, Evry), orchestrés avec **Airflow 3.3.2**, stockés dans **PostgreSQL 16**, le tout lancé avec Docker Compose.

Ce guide permet, après avoir cloné le dépôt, de démarrer l'environnement, de charger les données sources et de calculer les tables cibles. Les commandes sont à lancer dans **PowerShell**, depuis la racine du dépôt.

---

## 1. Prérequis

- **Git**
- **Docker Desktop**, démarré, avec au moins 4 Go de mémoire alloués (*Settings > Resources*).
- Ports libres sur la machine : **8080** (interface Airflow) et **5433** (base du projet).

Vérification :

```powershell
git --version
docker compose version
```

## 2. Cloner le dépôt sur la branche `develop`

```powershell
git clone -b develop https://github.com/SLIMENE-Malak/projet-qualite-donnees.git
cd projet-qualite-donnees
```

Toujours travailler à partir de `develop`, jamais de `main` (voir la section 8).

## 3. Créer le fichier `.env`

Les mots de passe et les clés ne sont **pas** dans le dépôt, qui est public. Chacun crée son propre `.env` à partir du modèle :

```powershell
Copy-Item .env.example .env
```

Ouvrir `.env` et remplacer **toutes** les valeurs `a_generer` et `changer_moi`. Il n'est pas nécessaire de modifier `AIRFLOW_UID` ni `PROJET_DB_USER`.

**Clé Fernet** : copier le résultat dans `AIRFLOW__CORE__FERNET_KEY`.

```powershell
docker run --rm apache/airflow:3.3.2 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Clés API et JWT** : lancer la commande **deux fois** et copier une valeur différente dans `AIRFLOW__API__SECRET_KEY`, puis dans `AIRFLOW__API_AUTH__JWT_SECRET`.

```powershell
docker run --rm apache/airflow:3.3.2 python -c "import secrets; print(secrets.token_hex(32))"
```

**Mots de passe** : choisir `_AIRFLOW_WWW_USER_PASSWORD` (compte de l'interface), `POSTGRES_AIRFLOW_PASSWORD` et `PROJET_DB_PASSWORD`. Utiliser seulement des lettres et des chiffres : les caractères `@ : / ?` cassent l'URI de connexion.

> `.env` est ignoré par Git : il ne doit jamais être commité ni partagé. S'il manque une variable, `docker compose` refuse de démarrer et indique laquelle.

## 4. Démarrer l'environnement

```powershell
docker compose up -d
```

Le premier démarrage télécharge les images et initialise les bases, ce qui prend quelques minutes. Au passage :

- `airflow-init` crée la base interne d'Airflow et le compte administrateur défini dans `.env` ;
- `postgres-projet` crée la base `qualite_donnees` et ses schémas (`s1`, `s2`, `s3`, `s4`, `cible`, `qualite`) avec `init-db/01_schemas.sql`.

Vérifier que tous les services sont `healthy`. `airflow-init` doit afficher `Exited (0)`, c'est normal :

```powershell
docker compose ps -a
```

Vérifier qu'aucun DAG n'est en erreur :

```powershell
docker compose exec airflow-dag-processor airflow dags list-import-errors
```

La réponse attendue est `No data found`.

Interface Airflow : <http://localhost:8080>, avec les identifiants `_AIRFLOW_WWW_USER_USERNAME` / `_AIRFLOW_WWW_USER_PASSWORD` de `.env`.

## 5. Charger les sources et calculer les cibles

Deux DAGs, à lancer dans cet ordre :

| DAG                  | Rôle                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------ |
| `chargement_sources` | Recrée les tables `s1` à `s4` et y copie les CSV de `data/`                               |
| `calcul_cibles`      | Calcule `cible.consommation_iris_paris`, `cible.consommation_iris_evry`, `cible.consommation_csp` |

En ligne de commande :

```powershell
docker compose exec airflow-scheduler airflow dags test chargement_sources
docker compose exec airflow-scheduler airflow dags test calcul_cibles
```

Chaque commande doit se terminer par `state=success`. On peut aussi passer par l'interface : activer le DAG (il est en pause à sa création), puis cliquer sur *Trigger*.

Les deux DAGs peuvent être relancés autant de fois que nécessaire : ils recréent les tables sans dupliquer les données.

## 6. Vérifier le contenu de la base

**En ligne de commande** (`\q` pour quitter) :

```powershell
docker compose exec postgres-projet psql -U projet -d qualite_donnees
```

**Avec un client graphique** (DBeaver, pgAdmin, extension PostgreSQL de VS Code) :

| Paramètre    | Valeur                                    |
| ------------ | ----------------------------------------- |
| Hôte         | `localhost`                               |
| Port         | `5433`                                    |
| Base         | `qualite_donnees`                         |
| Utilisateur  | `PROJET_DB_USER` de `.env` (`projet`)     |
| Mot de passe | `PROJET_DB_PASSWORD` de `.env`            |

Requête de contrôle :

```sql
SELECT 's1.population' AS table_chargee, count(*) FROM s1.population
UNION ALL SELECT 's1.consommation', count(*) FROM s1.consommation
UNION ALL SELECT 's2.population', count(*) FROM s2.population
UNION ALL SELECT 's2.consommation', count(*) FROM s2.consommation
UNION ALL SELECT 's3.csp', count(*) FROM s3.csp
UNION ALL SELECT 's4.iris', count(*) FROM s4.iris
UNION ALL SELECT 'cible.consommation_iris_paris', count(*) FROM cible.consommation_iris_paris
UNION ALL SELECT 'cible.consommation_iris_evry', count(*) FROM cible.consommation_iris_evry
UNION ALL SELECT 'cible.consommation_csp', count(*) FROM cible.consommation_csp;
```

Résultat attendu :

| Table                          | Lignes |
| ------------------------------ | ------ |
| s1 et s2, population et consommation | 50 chacune |
| s3.csp                         | 6      |
| s4.iris                        | 20     |
| cible.consommation_iris_paris  | 10     |
| cible.consommation_iris_evry   | 10     |
| cible.consommation_csp         | 1      |

> **`consommation_csp` ne contient qu'une ligne : ce n'est pas un bug.** Les CSV de `data/` contiennent volontairement des défauts : codes postaux `999`, rues vides, valeurs manquantes, CSP inconnue, adresses écrites différemment entre Population et Consommation. C'est ce que les pipelines d'audit vont mesurer et ce que les pipelines de nettoyage vont corriger. **Ne jamais modifier les fichiers de `data/`.**

## 7. Arrêter, redémarrer, repartir de zéro

```powershell
docker compose down      # arrête les conteneurs, les données sont conservées
docker compose up -d     # redémarre
```

Pour repartir d'une base vide, par exemple après une modification de `init-db/01_schemas.sql` ou des mots de passe de `.env` :

```powershell
docker compose down -v   # ATTENTION : supprime les volumes, donc les bases et l'historique Airflow
docker compose up -d
```

Relancer ensuite les DAGs de la section 5.

## 8. Travailler à plusieurs

- `main` contient les versions stables. `develop` est la branche d'intégration.
- Une branche par facteur de qualité, créée depuis `develop` :

  ```powershell
  git switch develop
  git pull
  git switch -c facteur/completude
  ```

- Les pull requests se font vers `develop`, jamais vers `main`.
- Sur une branche de facteur, ne modifier que les fichiers de ce facteur (`dags/audit_<facteur>.py`, `dags/nettoyage_<facteur>.py`, `dags/sql/audit/<facteur>.sql`, `dags/sql/nettoyage/<facteur>.sql`). **Prévenir le groupe** avant de toucher aux fichiers communs :
  - `docker-compose.yaml`, `config/airflow.cfg`, `.env.example` ;
  - `init-db/01_schemas.sql` ;
  - `dags/chargement_sources.py`, `dags/calcul_cibles.py`, `dags/sql/chargement/`, `dags/sql/cibles/` ;
  - tables du schéma `qualite`.
- Après chaque modification d'un DAG, vérifier les erreurs d'import (section 4).
- Aucun secret dans le code : toute nouvelle variable secrète va dans `.env`, avec une valeur fictive dans `.env.example`.

## 9. Organisation du dépôt

```
docker-compose.yaml        Services : Airflow, Postgres interne d'Airflow, postgres-projet, Redis
.env.example               Modèle de .env (valeurs fictives)
config/airflow.cfg         Configuration Airflow (sans clé)
init-db/01_schemas.sql     Création des schémas, au premier démarrage de postgres-projet
data/                      CSV sources, à ne pas modifier
dags/
  chargement_sources.py    CSV -> s1..s4
  calcul_cibles.py         s1..s4 -> cible.*
  sql/
    chargement/            Création des tables sources et COPY des CSV
    cibles/                Requêtes des trois tables cibles
    audit/                 Requêtes d'audit, une par facteur (à venir)
    nettoyage/             Requêtes de nettoyage, une par facteur (à venir)
```

## 10. Problèmes fréquents

| Symptôme | Cause et solution |
| --- | --- |
| `required variable ... is missing a value` au `docker compose up` | Variable absente ou vide dans `.env`. La compléter (section 3). |
| `port is already allocated` (8080 ou 5433) | Un autre programme utilise le port, par exemple un Postgres local. L'arrêter ou changer le port dans `docker-compose.yaml`, sans commiter ce changement. |
| `password authentication failed` | Le mot de passe de `.env` a changé après la création du volume. Remettre l'ancien, ou repartir de zéro avec `docker compose down -v` (section 7). |
| Un DAG n'apparaît pas dans l'interface | Attendre environ 30 secondes, puis vérifier les erreurs d'import (section 4). |
| Les services restent en `starting` ou redémarrent en boucle | Mémoire insuffisante : augmenter la mémoire de Docker Desktop (4 Go minimum). Consulter les journaux avec `docker compose logs airflow-scheduler`. |
| Une commande `docker compose exec` échoue avec `service is not running` | Lancer `docker compose up -d` d'abord. |
