FROM python:3.12-slim

WORKDIR /app

# Dépendances système nécessaires pour compiler certains packages Python (bcrypt, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python en premier (layer caché si requirements.txt ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Rendre l'entrypoint exécutable
RUN chmod +x docker/entrypoint.sh

# Port Streamlit
EXPOSE 8501

ENTRYPOINT ["/bin/bash", "docker/entrypoint.sh"]
