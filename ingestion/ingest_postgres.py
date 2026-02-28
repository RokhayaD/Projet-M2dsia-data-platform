"""
INGESTION PostgreSQL → MinIO Bronze
Ingère toutes les tables relationnelles en JSON dans le bucket bronze/
"""

import os
import json
import logging
from datetime import datetime, date
from decimal import Decimal

import psycopg2
import psycopg2.extras
from minio import Minio
from io import BytesIO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def json_serial(obj):
    """Sérialisation JSON pour types spéciaux Python."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type non sérialisable : {type(obj)}")


def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "universite"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin123")
    )


def get_minio_client():
    return Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
        secure=False
    )


def ingest_table(cursor, minio_client, table_name: str, extraction_ts: str):
    """Ingère une table PostgreSQL complète vers bronze/postgres/<table>/<ts>.json"""
    logger.info(f"📥 Ingestion table : {table_name}")
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    data = {
        "source": "postgresql",
        "database": "universite",
        "table": table_name,
        "extracted_at": extraction_ts,
        "row_count": len(rows),
        "records": [dict(row) for row in rows]
    }

    json_bytes = json.dumps(data, default=json_serial, ensure_ascii=False, indent=2).encode("utf-8")
    object_name = f"postgres/{table_name}/{extraction_ts}.json"

    minio_client.put_object(
        bucket_name="bronze",
        object_name=object_name,
        data=BytesIO(json_bytes),
        length=len(json_bytes),
        content_type="application/json"
    )
    logger.info(f"✅ {table_name} → bronze/{object_name} ({len(rows)} lignes)")
    return len(rows)


def run():
    logger.info("=" * 60)
    logger.info("INGESTION PostgreSQL → Bronze (démarrage)")
    logger.info("=" * 60)

    extraction_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tables = ["departements", "enseignants", "etudiants", "cours", "inscriptions", "notes", "salles"]

    conn = get_postgres_connection()
    minio_client = get_minio_client()

    total_rows = 0
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        for table in tables:
            try:
                rows = ingest_table(cursor, minio_client, table, extraction_ts)
                total_rows += rows
            except Exception as e:
                logger.error(f"❌ Erreur table {table} : {e}")

    conn.close()
    logger.info(f"\n✅ Ingestion PostgreSQL terminée — {total_rows} lignes ingérées")
    return total_rows


if __name__ == "__main__":
    run()
