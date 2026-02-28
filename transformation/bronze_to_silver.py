"""
TRANSFORMATION Bronze → Silver (couche nettoyée)
- Suppression des doublons
- Normalisation des types de données
- Validation et filtrage des données invalides
- Enrichissement basique (colonnes calculées)
"""

import os
import json
import logging
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")


def create_spark_session():
    spark = SparkSession.builder \
        .appName("DSIA_Bronze_to_Silver") \
        .config("spark.hadoop.fs.s3a.endpoint", f"http://{MINIO_ENDPOINT}") \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_bronze_json(spark, path: str):
    """Lit un fichier JSON de la couche Bronze."""
    return spark.read.option("multiline", "true").json(f"s3a://bronze/{path}")


def write_silver_parquet(df, path: str):
    """Écrit un DataFrame en Parquet dans la couche Silver."""
    df.write.mode("overwrite").parquet(f"s3a://silver/{path}")
    logger.info(f"✅ Écrit → silver/{path} ({df.count()} lignes)")


def transform_etudiants(spark):
    """Nettoyage et enrichissement de la table étudiants."""
    logger.info("🔄 Transformation : etudiants")

    df_raw = read_bronze_json(spark, "postgres/etudiants/")
    df = spark.read.json(df_raw.select(F.explode("records").alias("r")).select("r.*").rdd.map(
        lambda row: json.dumps(row.asDict())
    ))

    df = df \
        .dropDuplicates(["matricule"]) \
        .filter(F.col("email").isNotNull()) \
        .filter(F.col("statut").isin(["actif", "suspendu", "diplome"])) \
        .withColumn("email", F.lower(F.trim(F.col("email")))) \
        .withColumn("nom", F.upper(F.trim(F.col("nom")))) \
        .withColumn("prenom", F.initcap(F.trim(F.col("prenom")))) \
        .withColumn("nom_complet", F.concat_ws(" ", F.col("prenom"), F.col("nom"))) \
        .withColumn("est_boursier_potentiel",
                    F.when(F.col("moyenne_generale") >= 14.0, True).otherwise(False)) \
        .withColumn("niveau",
                    F.when(F.col("annee_etude") == 1, "L1")
                     .when(F.col("annee_etude") == 2, "L2")
                     .when(F.col("annee_etude") == 3, "L3")
                     .when(F.col("annee_etude") == 4, "M1")
                     .when(F.col("annee_etude") == 5, "M2")
                     .otherwise("Inconnu")) \
        .withColumn("silver_processed_at", F.lit(datetime.now().isoformat()))

    write_silver_parquet(df, "etudiants/")
    return df


def transform_cours(spark):
    """Nettoyage des cours."""
    logger.info("🔄 Transformation : cours")

    df_raw = read_bronze_json(spark, "postgres/cours/")
    df = spark.read.json(df_raw.select(F.explode("records").alias("r")).select("r.*").rdd.map(
        lambda row: json.dumps(row.asDict())
    ))

    df = df \
        .dropDuplicates(["code"]) \
        .filter(F.col("intitule").isNotNull()) \
        .withColumn("code", F.upper(F.trim(F.col("code")))) \
        .withColumn("heures_total",
                    F.col("heures_cm") + F.col("heures_td") + F.col("heures_tp")) \
        .withColumn("silver_processed_at", F.lit(datetime.now().isoformat()))

    write_silver_parquet(df, "cours/")
    return df


def transform_notes(spark):
    """Nettoyage et validation des notes."""
    logger.info("🔄 Transformation : notes")

    df_raw = read_bronze_json(spark, "postgres/notes/")
    df = spark.read.json(df_raw.select(F.explode("records").alias("r")).select("r.*").rdd.map(
        lambda row: json.dumps(row.asDict())
    ))

    df = df \
        .dropDuplicates(["etudiant_id", "cours_id", "annee_academique"]) \
        .filter(F.col("note_finale").isNotNull()) \
        .filter((F.col("note_finale") >= 0) & (F.col("note_finale") <= 20)) \
        .withColumn("est_admis", F.when(F.col("note_finale") >= 10.0, True).otherwise(False)) \
        .withColumn("mention_calculee",
                    F.when(F.col("note_finale") >= 16, "Très Bien")
                     .when(F.col("note_finale") >= 14, "Bien")
                     .when(F.col("note_finale") >= 12, "Assez Bien")
                     .when(F.col("note_finale") >= 10, "Passable")
                     .otherwise("Ajourné")) \
        .withColumn("silver_processed_at", F.lit(datetime.now().isoformat()))

    write_silver_parquet(df, "notes/")
    return df


def transform_inscriptions(spark):
    logger.info("🔄 Transformation : inscriptions")
    df_raw = read_bronze_json(spark, "postgres/inscriptions/")
    df = spark.read.json(df_raw.select(F.explode("records").alias("r")).select("r.*").rdd.map(
        lambda row: json.dumps(row.asDict())
    ))
    df = df \
        .dropDuplicates(["etudiant_id", "cours_id", "annee_academique"]) \
        .withColumn("silver_processed_at", F.lit(datetime.now().isoformat()))
    write_silver_parquet(df, "inscriptions/")
    return df


def transform_departements(spark):
    logger.info("🔄 Transformation : departements")
    df_raw = read_bronze_json(spark, "postgres/departements/")
    df = spark.read.json(df_raw.select(F.explode("records").alias("r")).select("r.*").rdd.map(
        lambda row: json.dumps(row.asDict())
    ))
    df = df \
        .dropDuplicates(["code"]) \
        .withColumn("code", F.upper(F.col("code"))) \
        .withColumn("silver_processed_at", F.lit(datetime.now().isoformat()))
    write_silver_parquet(df, "departements/")
    return df


def transform_feedbacks(spark):
    """Nettoyage des feedbacks MongoDB."""
    logger.info("🔄 Transformation : feedbacks_cours")
    df_raw = read_bronze_json(spark, "mongo/feedbacks_cours/")
    df = spark.read.json(df_raw.select(F.explode("records").alias("r")).select("r.*").rdd.map(
        lambda row: json.dumps(row.asDict())
    ))
    df = df \
        .filter(F.col("cours_code").isNotNull()) \
        .filter((F.col("note_globale") >= 0) & (F.col("note_globale") <= 5)) \
        .withColumn("satisfait", F.when(F.col("note_globale") >= 3.5, True).otherwise(False)) \
        .withColumn("silver_processed_at", F.lit(datetime.now().isoformat()))
    write_silver_parquet(df, "feedbacks_cours/")
    return df


def transform_absences(spark):
    """Nettoyage des absences depuis l'API."""
    logger.info("🔄 Transformation : absences (API)")
    df_raw = read_bronze_json(spark, "api/absences/")
    df = spark.read.json(
        df_raw.select(F.explode("data.absences").alias("r")).select("r.*").rdd.map(
            lambda row: json.dumps(row.asDict())
        )
    )
    df = df \
        .dropDuplicates(["id"]) \
        .withColumn("date", F.to_date(F.col("date"))) \
        .withColumn("silver_processed_at", F.lit(datetime.now().isoformat()))
    write_silver_parquet(df, "absences/")
    return df


def transform_bourses(spark):
    """Nettoyage des bourses depuis l'API."""
    logger.info("🔄 Transformation : bourses (API)")
    df_raw = read_bronze_json(spark, "api/bourses_2024_2025/")
    df = spark.read.json(
        df_raw.select(F.explode("data.bourses").alias("r")).select("r.*").rdd.map(
            lambda row: json.dumps(row.asDict())
        )
    )
    df = df \
        .dropDuplicates(["id"]) \
        .withColumn("montant_annuel", F.col("montant_mensuel") * F.col("duree_mois")) \
        .withColumn("silver_processed_at", F.lit(datetime.now().isoformat()))
    write_silver_parquet(df, "bourses/")
    return df


if __name__ == "__main__":
    logger.info("╔══════════════════════════════════════════╗")
    logger.info("║   TRANSFORMATION : Bronze → Silver       ║")
    logger.info("╚══════════════════════════════════════════╝")

    spark = create_spark_session()

    transformations = [
        ("etudiants", transform_etudiants),
        ("cours", transform_cours),
        ("notes", transform_notes),
        ("inscriptions", transform_inscriptions),
        ("departements", transform_departements),
        ("feedbacks", transform_feedbacks),
        ("absences", transform_absences),
        ("bourses", transform_bourses),
    ]

    for name, fn in transformations:
        try:
            fn(spark)
        except Exception as e:
            logger.error(f"❌ Erreur transformation {name} : {e}")

    spark.stop()
    logger.info("✅ Bronze → Silver terminé")
