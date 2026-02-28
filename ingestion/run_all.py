"""
Point d'entrée principal — Lance toutes les ingestions dans l'ordre.
Bronze Layer : PostgreSQL + MongoDB + API REST
"""

import time
import logging
import ingest_postgres
import ingest_mongo
import ingest_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def wait_for_services(retries=10, delay=5):
    """Attente que les services soient prêts."""
    import psycopg2, os, requests
    from pymongo import MongoClient

    # Vérification PostgreSQL
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", 5432)),
                dbname=os.getenv("POSTGRES_DB", "universite"),
                user=os.getenv("POSTGRES_USER", "admin"),
                password=os.getenv("POSTGRES_PASSWORD", "admin123")
            )
            conn.close()
            logger.info("✅ PostgreSQL prêt")
            break
        except Exception:
            logger.info(f"⏳ Attente PostgreSQL... ({i+1}/{retries})")
            time.sleep(delay)

    # Vérification MongoDB
    for i in range(retries):
        try:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/universite_nosql?authSource=admin")
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            client.admin.command('ping')
            client.close()
            logger.info("✅ MongoDB prêt")
            break
        except Exception:
            logger.info(f"⏳ Attente MongoDB... ({i+1}/{retries})")
            time.sleep(delay)

    # Vérification API REST
    api_url = os.getenv("API_URL", "http://localhost:8000")
    for i in range(retries):
        try:
            resp = requests.get(f"{api_url}/health", timeout=5)
            resp.raise_for_status()
            logger.info("✅ API REST prête")
            break
        except Exception:
            logger.info(f"⏳ Attente API REST... ({i+1}/{retries})")
            time.sleep(delay)

    # Vérification MinIO
    from minio import Minio
    for i in range(retries):
        try:
            minio_client = Minio(
                os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
                secure=False
            )
            minio_client.list_buckets()
            logger.info("✅ MinIO prêt")
            break
        except Exception:
            logger.info(f"⏳ Attente MinIO... ({i+1}/{retries})")
            time.sleep(delay)


if __name__ == "__main__":
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║         DATA PLATFORM — INGESTION LAYER (BRONZE)        ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")

    wait_for_services()

    logger.info("\n── Étape 1/3 : Ingestion PostgreSQL ──")
    try:
        ingest_postgres.run()
    except Exception as e:
        logger.error(f"❌ Échec ingestion PostgreSQL : {e}")

    logger.info("\n── Étape 2/3 : Ingestion MongoDB ──")
    try:
        ingest_mongo.run()
    except Exception as e:
        logger.error(f"❌ Échec ingestion MongoDB : {e}")

    logger.info("\n── Étape 3/3 : Ingestion API REST ──")
    try:
        ingest_api.run()
    except Exception as e:
        logger.error(f"❌ Échec ingestion API : {e}")

    logger.info("\n╔══════════════════════════════════════════════════════════╗")
    logger.info("║           INGESTION BRONZE COMPLÈTE ✅                   ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
