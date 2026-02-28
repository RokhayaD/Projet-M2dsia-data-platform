# Data Platform Universitaire — Projet M2DSIA

> **Data Engineer** | Domaine : Universitaire | Stack : Docker · Python · Spark · MinIO · PostgreSQL · MongoDB

---

## Contexte

Ce projet met en place une **data-plateforme complète** pour une université.
Elle gère l'ingestion, la transformation et l'exposition des données pour la **BI** et l'**IA**.

---

## Architecture Medallion

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│   SOURCES             BRONZE          SILVER          GOLD        │
│                                                                   │
│  PostgreSQL ──┐                                                   │
│  (étudiants,  │                                                   │
│   notes,      ├──► MinIO/bronze ──► MinIO/silver ──► MinIO/gold  │
│   cours...)   │      (JSON)          (Parquet)       (Parquet)   │
│               │                                                   │
│  MongoDB ─────┤    Données        Données           Data Marts   │
│  (candidatures│    brutes         nettoyées         agrégés BI   │
│   feedbacks,  │    telles         déduplicées                    │
│   événements) │    quelles        typées                         │
│               │                                                   │
│  API REST ────┘                                                   │
│  (absences,                                                       │
│   bourses,                                                        │
│   emplois dt)                                                     │
│                                                                   │
│                          Jupyter Notebook                         │
│                        (Visualisation BI) ◄── Gold Layer         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sources de Données (3 types)

| # | Type | Technologie | Données |
|---|------|-------------|---------|
| 1 | **Relationnelle** | PostgreSQL | Étudiants, Enseignants, Cours, Notes, Inscriptions, Départements |
| 2 | **Non-relationnelle** | MongoDB | Candidatures, Événements campus, Feedbacks cours |
| 3 | **API REST** | FastAPI (interne) | Emplois du temps, Absences, Bourses, Statistiques |

---

## Structure du Projet

```
projet-dsia/
├── docker-compose.yml          # Orchestration de tous les services
│
├── data/
│   ├── init_postgres.sql       # Schéma + données PostgreSQL
│   └── init_mongo.js           # Collections + données MongoDB
│
├── api/
│   ├── main.py                 # API REST FastAPI (Source 3)
│   └── Dockerfile
│
├── ingestion/
│   ├── ingest_postgres.py      # Ingestion PostgreSQL → Bronze
│   ├── ingest_mongo.py         # Ingestion MongoDB → Bronze
│   ├── ingest_api.py           # Ingestion API REST → Bronze
│   ├── run_all.py              # Point d'entrée ingestion
│   ├── requirements.txt
│   └── Dockerfile
│
├── transformation/
│   ├── bronze_to_silver.py     # Nettoyage Bronze → Silver (Spark)
│   ├── silver_to_gold.py       # Agrégation Silver → Gold (Spark)
│   ├── run_transformations.sh
│   └── Dockerfile
│
└── notebooks/
    └── analyse_gold.ipynb      # Visualisation BI couche Gold
```

---

##  Démarrage Rapide

### Prérequis
- Docker Desktop installé et démarré
- Au moins 6 Go de RAM disponibles

### Lancer le projet

```bash
# Cloner ou décompresser le projet
cd dsia-data-platform

# Lancer toute la stack
docker-compose up -d

# Suivre les logs d'ingestion
docker logs -f dsia_ingestion

# Suivre les logs de transformation
docker logs -f dsia_transformation
```

### Accéder aux interfaces

| Service | URL | Identifiants |
|---------|-----|--------------|
| **MinIO Console** (buckets Bronze/Silver/Gold) | http://localhost:9001 | minioadmin / minioadmin123 |
| **Jupyter Notebook** (BI) | http://localhost:8888 | *(pas de mot de passe)* |
| **API REST** (Swagger) | http://localhost:8000/docs | — |
| **Spark UI** | http://localhost:8080 | — |

### Ordre de démarrage automatique

```
1. PostgreSQL + MongoDB + API  (sources)
2. MinIO + création des buckets (bronze, silver, gold)
3. Ingestion Python (→ bronze)
4. Transformation Spark (bronze→silver→gold)
5. Jupyter disponible pour la BI
```

---

## Pipeline de Données

### Couche Bronze (Ingestion)
- **ingest_postgres.py** : lit les 7 tables PostgreSQL, les sérialise en JSON horodaté, les stocke dans `bronze/postgres/<table>/<timestamp>.json`
- **ingest_mongo.py** : lit les 3 collections MongoDB (ObjectId/dates sérialisés), stocke dans `bronze/mongo/<collection>/<timestamp>.json`
- **ingest_api.py** : consomme 5 endpoints REST (emplois du temps, absences, bourses, statistiques + variantes filtrées), stocke dans `bronze/api/<endpoint>/<timestamp>.json`

### Couche Silver (Nettoyage Spark)
Traitements appliqués :
- Suppression des doublons (`dropDuplicates`)
- Filtrage des lignes invalides (emails nuls, notes hors [0-20]...)
- Normalisation : `email` en minuscule, `nom` en majuscule, `code` en majuscule
- Colonnes calculées : `nom_complet`, `niveau` (L1..M2), `est_admis`, `mention_calculee`, `montant_annuel`
- Stockage en **Parquet** (compression, lecture rapide)

### Couche Gold (Agrégation Spark — Data Marts BI)

| Data Mart | Description |
|-----------|-------------|
| `dm_etudiants_complet` | Vue 360° : notes + absences + bourse par étudiant |
| `dm_performance_cours` | Moyenne, taux de réussite, nb inscrits par cours |
| `dm_stats_departement` | KPIs par département (étudiants, budget, moyenne) |
| `dm_etudiants_risque` | Score de risque basé absences + notes faibles |
| `dm_satisfaction_cours` | Taux satisfaction/recommandation (feedbacks MongoDB) |

---

## Exploration BI (Jupyter)

Ouvrir http://localhost:8888, puis `work/analyse_gold.ipynb`.

Le notebook contient 5 analyses visuelles :
1. Statistiques par département (histogrammes)
2. Distribution des moyennes étudiantes
3. Carte des étudiants à risque
4. Performance et taux de réussite par cours
5. Satisfaction et recommandation des cours

---

##  Stack Technique

| Composant | Rôle | Image |
|-----------|------|-------|
| **PostgreSQL 15** | Source relationnelle | `postgres:15` |
| **MongoDB 6** | Source non-relationnelle | `mongo:6` |
| **FastAPI** | API REST (Source 3) | `python:3.11-slim` |
| **MinIO** | Stockage objet (Bronze/Silver/Gold) | `minio/minio:latest` |
| **Apache Spark 3.5** | Moteur de transformation | `apache/spark:3.5.4` |
| **Python 3.11** | Scripts d'ingestion | `python:3.11-slim` |
| **Jupyter PySpark** | Notebook BI | `quay.io/jupyter/pyspark-notebook` |

---

## Bonnes Pratiques Appliquées

- **Séparation des responsabilités** : ingestion / transformation / exposition bien distincts
- **Idempotence** : chaque ingestion est horodatée, les transformations sont en mode `overwrite`
- **Healthchecks** : tous les services ont des healthchecks Docker
- **Ordre de démarrage** : `depends_on` + `condition: service_healthy`
- **Sérialisation robuste** : gestion des types Python spéciaux (datetime, Decimal, ObjectId)
- **Format Parquet** : Silver et Gold en Parquet (compression, schéma typé, lecture rapide)
- **Logging** : chaque script a des logs clairs avec niveaux INFO/ERROR
- **Variables d'environnement** : aucune credentials en dur dans le code

---

## Axes d'Amélioration

1. **Orchestration** : Ajouter Apache Airflow pour planifier les pipelines (ingestion quotidienne, etc.)
2. **Streaming** : Intégrer Apache Kafka pour les données temps réel (présences en cours, connexions)
3. **Qualité des données** : Ajouter Great Expectations pour des tests de qualité automatisés
4. **Catalogue de données** : Apache Atlas ou DataHub pour documenter les métadonnées
5. **Monitoring** : Prometheus + Grafana pour surveiller les performances du pipeline
6. **Sécurité** : Chiffrement des secrets avec HashiCorp Vault, TLS pour MinIO
7. **Delta Lake / Iceberg** : Remplacer Parquet par Delta Lake pour le versioning et les ACID transactions
8. **BI Dashboard** : Connecter Apache Superset ou Metabase sur la couche Gold

---

