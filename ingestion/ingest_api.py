"""
INGESTION API REST → MinIO Bronze
Consomme l'API interne et stocke les réponses JSON dans bronze/
"""

import os
import json
import logging
from datetime import datetime

import requests
from minio import Minio
from io import BytesIO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


API_URL = os.getenv("API_URL", "http://localhost:8000")

ENDPOINTS = [
    {"path": "/emplois-du-temps", "params": {}, "name": "emplois_du_temps"},
    {"path": "/emplois-du-temps", "params": {"departement": "INFO"}, "name": "emplois_du_temps_info"},
    {"path": "/absences", "params": {}, "name": "absences"},
    {"path": "/absences", "params": {"justifiee": False}, "name": "absences_non_justifiees"},
    {"path": "/bourses", "params": {"annee_academique": "2024-2025"}, "name": "bourses_2024_2025"},
    {"path": "/statistiques", "params": {}, "name": "statistiques_globales"},
]


def get_minio_client():
    return Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
        secure=False
    )


def fetch_and_store(minio_client, endpoint: dict, extraction_ts: str):
    """Appelle un endpoint REST et stocke la réponse dans bronze/api/"""
    url = f"{API_URL}{endpoint['path']}"
    logger.info(f"📥 Appel API : GET {url} | params={endpoint['params']}")

    response = requests.get(url, params=endpoint["params"], timeout=30)
    response.raise_for_status()

    data = {
        "source": "api_rest",
        "endpoint": endpoint["path"],
        "params": endpoint["params"],
        "extracted_at": extraction_ts,
        "http_status": response.status_code,
        "data": response.json()
    }

    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    object_name = f"api/{endpoint['name']}/{extraction_ts}.json"

    minio_client.put_object(
        bucket_name="bronze",
        object_name=object_name,
        data=BytesIO(json_bytes),
        length=len(json_bytes),
        content_type="application/json"
    )
    logger.info(f"✅ → bronze/{object_name}")
    return 1


def run():
    logger.info("=" * 60)
    logger.info("INGESTION API REST → Bronze (démarrage)")
    logger.info("=" * 60)

    extraction_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    minio_client = get_minio_client()

    success = 0
    for endpoint in ENDPOINTS:
        try:
            fetch_and_store(minio_client, endpoint, extraction_ts)
            success += 1
        except Exception as e:
            logger.error(f"❌ Erreur endpoint {endpoint['path']} : {e}")

    logger.info(f"\n✅ Ingestion API terminée — {success}/{len(ENDPOINTS)} endpoints ingérés")
    return success


if __name__ == "__main__":
    run()
