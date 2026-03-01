# RAG Intelligence — Guide d'utilisation

## Démarrage rapide (Docker)

```bash
# 1. Copier et configurer l'environnement
cp .env.example .env
# Optionnel : ajouter GEMINI_API_KEY dans .env pour utiliser Gemini

# 2. Lancer tous les services
cd docker
docker compose up -d

# 3. Attendre que les modèles soient téléchargés (première fois uniquement)
docker logs -f rag_ollama_init
# → Attendre "Tous les modèles sont disponibles ✓"

# 4. Ouvrir l'application
http://localhost:8501
```

---

## Connexion

| Utilisateur | Mot de passe | Rôle | Accès |
|-------------|--------------|------|-------|
| `alice` | `alice123` | guest | Documents publics uniquement |
| `bob` | `bob123` | employee | Documents publics + internes |
| `admin` | `admin123` | admin | Tous les documents (confidentiel inclus) |

---

## Utilisation

### 1. Choisir un LLM et une stratégie RAG (sidebar)

- **Language Model** : `mistral` · `qwen` · `llama` · `gemini`
- **RAG Strategy** : `simple` · `secure` · `hybrid` · `modular` · `reranking`

> `gemini` nécessite une `GEMINI_API_KEY` dans `.env`. Les autres modèles fonctionnent 100% en local.

### 2. Poser une question

Tapez votre question dans le champ de texte. L'app retourne la réponse et les sources utilisées.

---

## Exemples de questions

### Guest (`alice`) — accès public
- *"What are the general conditions of use of public services?"*
- *"What is your role?"*
- *"What can you do?"*

### Employee (`bob`) — accès interne
- *"What are the obligations of the parties in the contract?"*
- *"What is the scope of services in the contract?"*
- *"What are the general terms of the agreement?"*
- *"What are the responsibilities of the contractor?"*

### Admin — accès confidentiel
- *"What are the payment terms and fees?"*
- *"What are the penalties in case of late payment?"*
- *"What are the liability clauses?"*
- *"What is the compensation and indemnity policy?"*
- *"What are the termination conditions?"*

> Les questions confidentielles retournent "You do not have access to this type of information." pour alice et bob.

---

## Arrêter l'application

```bash
cd docker
docker compose down

# Supprimer aussi les modèles téléchargés (~15 GB) :
docker compose down -v
```
