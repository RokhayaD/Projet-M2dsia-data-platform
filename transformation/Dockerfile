FROM apache/spark:3.5.4

USER root
RUN pip install minio

COPY bronze_to_silver.py /app/bronze_to_silver.py
COPY silver_to_gold.py /app/silver_to_gold.py
COPY run_transformations.sh /app/run_transformations.sh
RUN chmod +x /app/run_transformations.sh

WORKDIR /app
CMD ["/bin/bash", "run_transformations.sh"]
