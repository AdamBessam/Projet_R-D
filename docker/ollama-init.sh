#!/bin/sh
set -e

echo ""
echo "=============================================="
echo "   Ollama Init — Téléchargement des modèles"
echo "   OLLAMA_HOST: ${OLLAMA_HOST}"
echo "=============================================="

# ==============================================================
# Attendre que le service Ollama soit disponible
# ==============================================================
echo ""
echo "Attente du service Ollama..."

until ollama list > /dev/null 2>&1; do
    echo "  Ollama pas encore prêt, attente 5s..."
    sleep 5
done

echo "  Service Ollama prêt ✓"
echo ""

# ==============================================================
# Pull des modèles
# Les modèles sont stockés dans le volume ollama_data (/root/.ollama)
# Si le modèle est déjà présent, ollama pull est quasi instantané.
# Premier téléchargement : peut prendre 10-30 min selon la connexion.
# ==============================================================

echo "Téléchargement de Mistral 7B..."
ollama pull mistral
echo "  Mistral 7B prêt ✓"
echo ""

echo "Téléchargement de Llama 3.1 8B..."
ollama pull llama3.1
echo "  Llama 3.1 8B prêt ✓"
echo ""

echo "Téléchargement de Qwen3 8B..."
ollama pull qwen3:8b
echo "  Qwen3 8B prêt ✓"
echo ""

echo "=============================================="
echo "   Tous les modèles sont disponibles ✓"
echo "=============================================="
