#!/bin/bash
echo "╔══════════════════════════════════════════════════════╗"
echo "║     DATA PLATFORM — TRANSFORMATION LAYER            ║"
echo "╚══════════════════════════════════════════════════════╝"

# L'ingestion est garantie terminée via depends_on: service_completed_successfully
sleep 5  # Court délai pour stabilisation MinIO

SPARK_SUBMIT=/opt/spark/bin/spark-submit

echo ""
echo "── Étape 1/2 : Bronze → Silver (nettoyage) ──"
$SPARK_SUBMIT \
  --master ${SPARK_MASTER:-local[*]} \
  --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  /app/bronze_to_silver.py

echo ""
echo "── Étape 2/2 : Silver → Gold (agrégation BI) ──"
$SPARK_SUBMIT \
  --master ${SPARK_MASTER:-local[*]} \
  --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  /app/silver_to_gold.py

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         TRANSFORMATIONS SILVER + GOLD COMPLETES ✅  ║"
echo "╚══════════════════════════════════════════════════════╝"
