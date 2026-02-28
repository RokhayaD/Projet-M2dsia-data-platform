FROM python:3.11-slim

WORKDIR /app

# Installer curl + dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --no-cache-dir fastapi "uvicorn[standard]"

# Copier le code
COPY main.py .

# Exposer le port
EXPOSE 8000

# Vérifier que curl est bien là
RUN curl --version

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
