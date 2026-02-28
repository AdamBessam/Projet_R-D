#!/bin/bash
set -e

echo ""
echo "=============================================="
echo "   RAG Legal App — Démarrage du container"
echo "=============================================="

# ==============================================================
# ÉTAPE 1 : Attendre que MySQL soit prêt
# ==============================================================
echo ""
echo "[1/5] Attente de MySQL (host: ${MYSQL_HOST:-mysql})..."

until python -c "
import mysql.connector, os, sys
try:
    c = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'mysql'),
        port=int(os.environ.get('MYSQL_PORT', '3306')),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', '')
    )
    c.close()
except Exception as e:
    sys.exit(1)
" 2>/dev/null; do
    echo "  MySQL pas encore prêt, nouvelle tentative dans 3s..."
    sleep 3
done

echo "  MySQL prêt ✓"

# ==============================================================
# ÉTAPE 2 : Initialiser la base de données et les utilisateurs
#   - setup_database.py : crée la BDD + la table users
#   - seed_users.py     : insère alice / bob / admin (bcrypt)
#   Idempotents — sans risque à chaque restart.
# ==============================================================
echo ""
echo "[2/5] Initialisation de la base de données..."

python scripts/setup_database.py
python scripts/seed_users.py

echo "  Base de données initialisée ✓"

# ==============================================================
# ÉTAPE 3 : Préparer le corpus
#   - Lit data/contracts.jsonl
#   - Classifie chaque clause (public / internal / confidential)
#   - Génère data/contracts_with_access.jsonl
#   → Ignoré si le fichier de sortie existe déjà
# ==============================================================
echo ""
echo "[3/5] Préparation du corpus..."

if [ -f "data/contracts_with_access.jsonl" ]; then
    echo "  contracts_with_access.jsonl déjà présent → étape ignorée ✓"
else
    echo "  Lancement de prepare_corpus.py..."
    python src/prepare_corpus.py
    echo "  Corpus préparé ✓"
fi

# ==============================================================
# ÉTAPE 4 : Indexation dans ChromaDB
#   - Lit data/contracts_with_access.jsonl
#   - Crée les embeddings (paraphrase-multilingual-mpnet-base-v2)
#   - Indexe dans db/
#   → Ignoré si db/chroma.sqlite3 existe déjà
#   ⚠ ingestion.py supprime et recrée db/ s'il tourne,
#     donc on ne le lance qu'une seule fois.
# ==============================================================
echo ""
echo "[4/5] Indexation ChromaDB..."

if [ -f "db/chroma.sqlite3" ]; then
    echo "  Index ChromaDB déjà présent (db/chroma.sqlite3) → étape ignorée ✓"
else
    echo "  Lancement de ingestion.py..."
    echo "  (Peut prendre plusieurs minutes — téléchargement du modèle + indexation)"
    python src/ingestion.py
    echo "  Indexation terminée ✓"
fi

# ==============================================================
# ÉTAPE 5 : Attendre Ollama (non bloquant — timeout 2 min)
#   Si Ollama n'est pas disponible, l'app démarre quand même
#   (Gemini cloud reste fonctionnel)
# ==============================================================
echo ""
echo "[5/5] Attente d'Ollama (timeout 120s)..."

WAITED=0
MAX_WAIT=120

until curl -sf http://ollama:11434/api/version > /dev/null 2>&1; do
    if [ "$WAITED" -ge "$MAX_WAIT" ]; then
        echo "  Ollama non disponible après ${MAX_WAIT}s."
        echo "  L'app démarre sans les modèles locaux (Gemini reste disponible)."
        break
    fi
    echo "  Ollama pas encore prêt... (${WAITED}s / ${MAX_WAIT}s)"
    sleep 5
    WAITED=$((WAITED + 5))
done

if curl -sf http://ollama:11434/api/version > /dev/null 2>&1; then
    echo "  Ollama prêt ✓"
fi

# ==============================================================
# LANCEMENT DE STREAMLIT
# ==============================================================
echo ""
echo "=============================================="
echo "   Streamlit → http://localhost:8501"
echo "=============================================="
echo ""

exec streamlit run src/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.fileWatcherType=none
