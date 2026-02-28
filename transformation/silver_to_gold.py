"""
TRANSFORMATION Silver → Gold (couche BI / analytique)
Création de Data Marts prêts à l'emploi pour la BI :
  1. gold/dm_etudiants_complet    → vue 360° d'un étudiant
  2. gold/dm_performance_cours    → performance par cours
  3. gold/dm_stats_departement    → stats par département
  4. gold/dm_etudiants_risque     → étudiants à risque (absences + notes)
  5. gold/dm_satisfaction_cours   → satisfaction des cours (feedbacks)
"""

import os
import logging
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")


def create_spark_session():
    spark = SparkSession.builder \
        .appName("DSIA_Silver_to_Gold") \
        .config("spark.hadoop.fs.s3a.endpoint", f"http://{MINIO_ENDPOINT}") \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_silver(spark, table: str):
    return spark.read.parquet(f"s3a://silver/{table}/")


def write_gold(df, name: str):
    df.write.mode("overwrite").parquet(f"s3a://gold/{name}/")
    logger.info(f"✅ Écrit → gold/{name}/ ({df.count()} lignes)")


def create_dm_etudiants_complet(spark):
    """Vue 360° d'un étudiant avec ses stats de notes, absences, bourses."""
    logger.info("🏆 Gold : dm_etudiants_complet")

    etudiants = read_silver(spark, "etudiants")
    notes = read_silver(spark, "notes")
    absences = read_silver(spark, "absences")
    departements = read_silver(spark, "departements")

    # Stats notes par étudiant
    notes_stats = notes.groupBy("etudiant_id").agg(
        F.avg("note_finale").alias("moyenne_notes"),
        F.count("*").alias("nb_cours_passes"),
        F.sum(F.when(F.col("est_admis") == True, 1).otherwise(0)).alias("nb_cours_admis"),
        F.min("note_finale").alias("note_min"),
        F.max("note_finale").alias("note_max")
    )

    # Stats absences par étudiant
    absences_stats = absences.groupBy("etudiant_matricule").agg(
        F.count("*").alias("nb_absences_total"),
        F.sum(F.when(F.col("justifiee") == False, 1).otherwise(0)).alias("nb_absences_non_justifiees")
    )

    dm = etudiants \
        .join(departements.select("id", F.col("nom").alias("departement_nom"), "code"),
              etudiants.departement_id == departements.id, "left") \
        .join(notes_stats, etudiants.id == notes_stats.etudiant_id, "left") \
        .join(absences_stats, etudiants.matricule == absences_stats.etudiant_matricule, "left") \
        .select(
            etudiants["id"], etudiants["matricule"], etudiants["nom_complet"],
            etudiants["email"], etudiants["annee_etude"], etudiants["niveau"],
            etudiants["statut"], etudiants["moyenne_generale"],
            F.col("departement_nom"), F.col("code").alias("departement_code"),
            F.round(F.col("moyenne_notes"), 2).alias("moyenne_notes_calculee"),
            F.col("nb_cours_passes"), F.col("nb_cours_admis"),
            F.when(F.col("nb_cours_passes") > 0,
                   F.round(F.col("nb_cours_admis") / F.col("nb_cours_passes") * 100, 1)
                   ).otherwise(None).alias("taux_reussite_pct"),
            F.coalesce(F.col("nb_absences_total"), F.lit(0)).alias("nb_absences"),
            F.coalesce(F.col("nb_absences_non_justifiees"), F.lit(0)).alias("nb_absences_injustifiees"),
            F.lit(datetime.now().isoformat()).alias("gold_processed_at")
        )

    write_gold(dm, "dm_etudiants_complet")


def create_dm_performance_cours(spark):
    """Performance par cours : moyenne, nb inscrits, taux de réussite."""
    logger.info("🏆 Gold : dm_performance_cours")

    cours = read_silver(spark, "cours")
    notes = read_silver(spark, "notes")
    inscriptions = read_silver(spark, "inscriptions")

    nb_inscrits = inscriptions.groupBy("cours_id").agg(
        F.count("*").alias("nb_inscrits")
    )

    stats_notes = notes.groupBy("cours_id").agg(
        F.avg("note_finale").alias("moyenne_classe"),
        F.count("*").alias("nb_notes"),
        F.sum(F.when(F.col("est_admis") == True, 1).otherwise(0)).alias("nb_admis"),
        F.stddev("note_finale").alias("ecart_type"),
        F.min("note_finale").alias("note_min"),
        F.max("note_finale").alias("note_max")
    )

    dm = cours \
        .join(nb_inscrits, cours.id == nb_inscrits.cours_id, "left") \
        .join(stats_notes, cours.id == stats_notes.cours_id, "left") \
        .select(
            cours["id"], cours["code"], cours["intitule"],
            cours["credits"], cours["heures_total"], cours["semestre"],
            cours["departement_id"],
            F.coalesce(F.col("nb_inscrits"), F.lit(0)).alias("nb_inscrits"),
            F.round(F.col("moyenne_classe"), 2).alias("moyenne_classe"),
            F.round(F.col("ecart_type"), 2).alias("ecart_type"),
            F.col("note_min"), F.col("note_max"),
            F.when(F.col("nb_notes") > 0,
                   F.round(F.col("nb_admis") / F.col("nb_notes") * 100, 1)
                   ).otherwise(None).alias("taux_reussite_pct"),
            F.lit(datetime.now().isoformat()).alias("gold_processed_at")
        )

    write_gold(dm, "dm_performance_cours")


def create_dm_stats_departement(spark):
    """Statistiques agrégées par département."""
    logger.info("🏆 Gold : dm_stats_departement")

    departements = read_silver(spark, "departements")
    etudiants = read_silver(spark, "etudiants")
    cours = read_silver(spark, "cours")

    stats_etu = etudiants.groupBy("departement_id").agg(
        F.count("*").alias("nb_etudiants"),
        F.sum(F.when(F.col("statut") == "actif", 1).otherwise(0)).alias("nb_actifs"),
        F.avg("moyenne_generale").alias("moyenne_dept"),
        F.sum(F.when(F.col("est_boursier_potentiel") == True, 1).otherwise(0)).alias("nb_boursiers_potentiels")
    )

    stats_cours = cours.groupBy("departement_id").agg(
        F.count("*").alias("nb_cours")
    )

    dm = departements \
        .join(stats_etu, departements.id == stats_etu.departement_id, "left") \
        .join(stats_cours, departements.id == stats_cours.departement_id, "left") \
        .select(
            departements["id"], departements["nom"], departements["code"],
            departements["responsable"], departements["budget"],
            F.coalesce(F.col("nb_etudiants"), F.lit(0)).alias("nb_etudiants"),
            F.coalesce(F.col("nb_actifs"), F.lit(0)).alias("nb_actifs"),
            F.round(F.col("moyenne_dept"), 2).alias("moyenne_departement"),
            F.coalesce(F.col("nb_boursiers_potentiels"), F.lit(0)).alias("nb_boursiers_potentiels"),
            F.coalesce(F.col("nb_cours"), F.lit(0)).alias("nb_cours"),
            F.lit(datetime.now().isoformat()).alias("gold_processed_at")
        )

    write_gold(dm, "dm_stats_departement")


def create_dm_etudiants_risque(spark):
    """Identification des étudiants à risque (absences élevées + notes faibles)."""
    logger.info("🏆 Gold : dm_etudiants_risque")

    etudiants = read_silver(spark, "etudiants")
    notes = read_silver(spark, "notes")
    absences = read_silver(spark, "absences")

    notes_moy = notes.groupBy("etudiant_id").agg(
        F.avg("note_finale").alias("moy_notes")
    )

    abs_count = absences.groupBy("etudiant_matricule").agg(
        F.count("*").alias("total_absences"),
        F.sum(F.when(F.col("justifiee") == False, 1).otherwise(0)).alias("abs_injustifiees")
    )

    dm = etudiants \
        .join(notes_moy, etudiants.id == notes_moy.etudiant_id, "left") \
        .join(abs_count, etudiants.matricule == abs_count.etudiant_matricule, "left") \
        .withColumn("score_risque",
                    F.coalesce(F.col("abs_injustifiees"), F.lit(0)) * 10 +
                    F.when(F.col("moy_notes").isNull(), 40)
                     .when(F.col("moy_notes") < 10, 50)
                     .when(F.col("moy_notes") < 12, 25)
                     .otherwise(0)) \
        .withColumn("niveau_risque",
                    F.when(F.col("score_risque") >= 60, "Critique")
                     .when(F.col("score_risque") >= 30, "Élevé")
                     .when(F.col("score_risque") >= 10, "Modéré")
                     .otherwise("Faible")) \
        .filter(F.col("statut") == "actif") \
        .select(
            "matricule", "nom_complet", "niveau", "departement_id",
            F.round("moy_notes", 2).alias("moyenne"),
            F.coalesce(F.col("total_absences"), F.lit(0)).alias("nb_absences"),
            F.coalesce(F.col("abs_injustifiees"), F.lit(0)).alias("absences_injustifiees"),
            "score_risque", "niveau_risque",
            F.lit(datetime.now().isoformat()).alias("gold_processed_at")
        ) \
        .orderBy(F.col("score_risque").desc())

    write_gold(dm, "dm_etudiants_risque")


def create_dm_satisfaction_cours(spark):
    """Satisfaction et retours sur les cours (depuis feedbacks MongoDB)."""
    logger.info("🏆 Gold : dm_satisfaction_cours")

    feedbacks = read_silver(spark, "feedbacks_cours")

    dm = feedbacks.groupBy("cours_code", "cours_intitule", "annee_academique").agg(
        F.count("*").alias("nb_repondants"),
        F.avg("note_globale").alias("note_globale_moy"),
        F.sum(F.when(F.col("recommande") == True, 1).otherwise(0)).alias("nb_recommandations"),
        F.sum(F.when(F.col("satisfait") == True, 1).otherwise(0)).alias("nb_satisfaits")
    ) \
        .withColumn("taux_recommandation_pct",
                    F.round(F.col("nb_recommandations") / F.col("nb_repondants") * 100, 1)) \
        .withColumn("taux_satisfaction_pct",
                    F.round(F.col("nb_satisfaits") / F.col("nb_repondants") * 100, 1)) \
        .withColumn("note_globale_moy", F.round(F.col("note_globale_moy"), 2)) \
        .withColumn("gold_processed_at", F.lit(datetime.now().isoformat()))

    write_gold(dm, "dm_satisfaction_cours")


if __name__ == "__main__":
    logger.info("╔══════════════════════════════════════════╗")
    logger.info("║   TRANSFORMATION : Silver → Gold (BI)    ║")
    logger.info("╚══════════════════════════════════════════╝")

    spark = create_spark_session()

    gold_tables = [
        ("dm_etudiants_complet", create_dm_etudiants_complet),
        ("dm_performance_cours", create_dm_performance_cours),
        ("dm_stats_departement", create_dm_stats_departement),
        ("dm_etudiants_risque", create_dm_etudiants_risque),
        ("dm_satisfaction_cours", create_dm_satisfaction_cours),
    ]

    for name, fn in gold_tables:
        try:
            fn(spark)
        except Exception as e:
            logger.error(f"❌ Erreur Gold {name} : {e}")

    spark.stop()
    logger.info("✅ Silver → Gold terminé — Data Marts prêts pour la BI !")
