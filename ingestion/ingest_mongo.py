"""
INGESTION MongoDB → MinIO Bronze
Ingère toutes les collections NoSQL en JSON dans le bucket bronze/
"""

import os
import json
import logging
from datetime import datetime

from pymongo import MongoClient
from bson import ObjectId
from minio import Minio
from io import BytesIO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def bson_serial(obj):
    """Sérialisation JSON pour types BSON (ObjectId, datetime)."""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type non sérialisable : {type(obj)}")


def get_mongo_client():
    uri = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/universite_nosql?authSource=admin")
    return MongoClient(uri)


def get_minio_client():
    return Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
        secure=False
    )


def ingest_collection(db, minio_client, collection_name: str, extraction_ts: str):
    """Ingère une collection MongoDB complète vers bronze/mongo/<collection>/<ts>.json"""
    logger.info(f"📥 Ingestion collection : {collection_name}")
    collection = db[collection_name]
    documents = list(collection.find())

    data = {
        "source": "mongodb",
        "database": "universite_nosql",
        "collection": collection_name,
        "extracted_at": extraction_ts,
        "doc_count": len(documents),
        "records": documents
    }

    json_bytes = json.dumps(data, default=bson_serial, ensure_ascii=False, indent=2).encode("utf-8")
    object_name = f"mongo/{collection_name}/{extraction_ts}.json"

    minio_client.put_object(
        bucket_name="bronze",
        object_name=object_name,
        data=BytesIO(json_bytes),
        length=len(json_bytes),
        content_type="application/json"
    )
    logger.info(f"✅ {collection_name} → bronze/{object_name} ({len(documents)} docs)")
    return len(documents)


def run():
    logger.info("=" * 60)
    logger.info("INGESTION MongoDB → Bronze (démarrage)")
    logger.info("=" * 60)

    extraction_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    collections = ["evenements", "candidatures", "feedbacks_cours"]

    mongo_client = get_mongo_client()
    db = mongo_client["universite_nosql"]
    minio_client = get_minio_client()

    total_docs = 0
    for col in collections:
        try:
            docs = ingest_collection(db, minio_client, col, extraction_ts)
            total_docs += docs
        except Exception as e:
            logger.error(f"❌ Erreur collection {col} : {e}")

    mongo_client.close()
    logger.info(f"\n✅ Ingestion MongoDB terminée — {total_docs} documents ingérés")
    return total_docs


if __name__ == "__main__":
    run()
