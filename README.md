# RAG Intelligence — Système RAG Sécurisé

Projet R&D d'un système **Retrieval-Augmented Generation (RAG) sécurisé** pour répondre à des questions sur des documents contractuels, avec contrôle d'accès par rôles et support de multiples modèles LLM locaux et cloud.

---

## Table des matières

- [Présentation du projet](#présentation-du-projet)
- [Architecture globale](#architecture-globale)
- [Structure des fichiers](#structure-des-fichiers)
- [Modèles LLM supportés](#modèles-llm-supportés)
- [Stratégies RAG](#stratégies-rag)
- [Système de sécurité et contrôle d'accès](#système-de-sécurité-et-contrôle-daccès)
- [Base documentaire](#base-documentaire)
- [Pipeline RAG — Fonctionnement détaillé](#pipeline-rag--fonctionnement-détaillé)
- [Support Multi-LLM — Pattern Factory](#support-multi-llm--pattern-factory)
- [Installation et démarrage](#installation-et-démarrage)
- [Utilisation](#utilisation)
- [Gestion des utilisateurs](#gestion-des-utilisateurs)
- [Ajouter un LLM ou une stratégie RAG](#ajouter-un-llm-ou-une-stratégie-rag)

---

## Présentation du projet

Ce projet répond à la problématique suivante :

> *Comment permettre à des utilisateurs avec des droits d'accès différents de poser des questions sur une base documentaire confidentielle, en combinant de manière flexible n'importe quel LLM avec n'importe quelle stratégie RAG ?*

### Fonctionnalités principales

- Ingestion et indexation vectorielle de documents contractuels (ChromaDB)
- 4 stratégies RAG modulaires et interchangeables
- 4 LLMs supportés (3 locaux via Ollama + 1 cloud via API)
- Authentification JWT + MySQL + bcrypt
- Contrôle d'accès hiérarchique (public / internal / confidential)
- Interface Streamlit moderne avec sélection dynamique LLM × RAG
- Fallback intelligent : si aucun document autorisé, le LLM répond uniquement sur son rôle

---

## Architecture globale

```
Utilisateur (Streamlit)
        │
        ▼
  Authentification JWT
  (username + password → MySQL → bcrypt → token)
        │
        ▼
  Niveau d'accès déterminé
  (guest → public | employee → internal | admin → confidential)
        │
        ▼
  Pipeline RAG (pipeline.py)
  ┌─────────────────────────────────────────┐
  │  1. RAG Strategy → retrieve(question)   │
  │     → secure_search() → ChromaDB        │
  │     → filtre par niveau d'accès         │
  │                                         │
  │  2. Si documents trouvés :              │
  │     → build_prompt(question, docs)      │
  │     → llm.generate(prompt)              │
  │                                         │
  │  3. Si aucun document autorisé :        │
  │     → system_prompt (rôle assistant)    │
  │     → llm.generate(system_prompt+query) │
  └─────────────────────────────────────────┘
        │
        ▼
  Réponse + Sources affichées dans Streamlit
```

---

## Structure des fichiers

```
Projet_R-D/
├── src/
│   ├── app.py                    # Interface Streamlit (UI principale)
│   ├── pipeline.py               # Orchestration du pipeline RAG
│   ├── factory.py                # Factory Pattern (LLM + RAG)
│   ├── search.py                 # Recherche vectorielle sécurisée
│   ├── ingestion.py              # Indexation documents → ChromaDB
│   ├── prepare_corpus.py         # Classification des documents par accès
│   ├── auth.py                   # Création/décodage JWT
│   ├── auth_service.py           # Authentification MySQL + bcrypt
│   ├── security.py               # Mapping rôle → niveau d'accès
│   ├── db_config.py              # Connexion MySQL
│   ├── reranker.py               # Cross-Encoder reranking
│   ├── evaluation_metrics.py     # Métriques d'évaluation RAG
│   ├── benchmark.py              # Benchmark LLM × RAG × questions
│   ├── benchmark_app.py          # Dashboard Streamlit des benchmarks
│   │
│   ├── llms/                     # Adaptateurs LLM
│   │   ├── base.py               # Classe abstraite LLM
│   │   ├── mistral.py            # Mistral via Ollama (local)
│   │   ├── llama.py              # Llama 3.1 8B via Ollama (local)
│   │   ├── qwen.py               # Qwen3 8B via Ollama (local)
│   │   └── gemini_llm.py         # Gemini 2.5 Flash via API Google
│   │
│   └── rag_strategies/           # Stratégies RAG
│       ├── base.py               # Classe abstraite RAGStrategy
│       ├── simple_rag.py         # Recherche sémantique basique
│       ├── secure_rag.py         # Avec refus explicite si non autorisé
│       ├── hybrid_rag.py         # Sémantique + lexical
│       ├── modular_rag.py        # Architecture extensible
│       └── reranking_rag.py      # Avec Cross-Encoder reranking
│
├── data/
│   ├── contracts.jsonl                # Corpus brut
│   ├── contracts_with_access.jsonl    # Corpus avec niveaux d'accès (521 docs)
│   └── test_questions.json            # Questions pour benchmark
│
├── db/                           # Base vectorielle ChromaDB (persistante)
├── reports/                      # Résultats de benchmark
├── scripts/                      # Scripts utilitaires
│   ├── setup_database.py         # Création base MySQL
│   ├── seed_users.py             # Création utilisateurs par défaut
│   ├── add_user.py               # Ajout interactif d'utilisateur
│   └── hash_password.py          # Utilitaire bcrypt
├── tests/
│   ├── test_search.py            # Tests logique ACL
│   └── test_rag.py               # Tests génération prompt
├── .env                          # Variables d'environnement
└── requirements.txt              # Dépendances Python
```

---

## Modèles LLM supportés

Tous les LLMs partagent la même interface abstraite (`generate(prompt) → str`) ce qui permet de les interchanger sans modifier le reste du code.

### Mistral — `src/llms/mistral.py`

- **Modèle** : `mistral` (7B paramètres)
- **Fournisseur** : Ollama (local, `http://localhost:11434`)
- **Coût** : Gratuit (100% local)
- **Confidentialité** : Maximale (aucune donnée envoyée à l'extérieur)
- **Téléchargement** : `ollama pull mistral`

### Llama 3.1 — `src/llms/llama.py`

- **Modèle** : `llama3.1:8b` (8B paramètres)
- **Fournisseur** : Ollama (local)
- **Coût** : Gratuit
- **Points forts** : Excellent en anglais, bon équilibre vitesse/qualité
- **Téléchargement** : `ollama pull llama3.1:8b`

### Qwen3 — `src/llms/qwen.py`

- **Modèle** : `qwen3:8b` (8B paramètres)
- **Fournisseur** : Ollama (local)
- **Coût** : Gratuit
- **Points forts** : Multilingue, mode "thinking" désactivé (`think: false`)
- **Téléchargement** : `ollama pull qwen3:8b`

### Gemini 2.5 Flash — `src/llms/gemini_llm.py`

- **Modèle** : `gemini-2.5-flash`
- **Fournisseur** : API Google (cloud)
- **Coût** : Quota gratuit généreux
- **Points forts** : Contexte 1M tokens, très rapide
- **Requis** : `GEMINI_API_KEY` dans `.env`

### Tableau comparatif

| Critère | Mistral | Llama 3.1 | Qwen3 | Gemini |
|---------|---------|-----------|-------|--------|
| Hébergement | Local | Local | Local | Cloud |
| Coût | Gratuit | Gratuit | Gratuit | Quota gratuit |
| Confidentialité | Maximale | Maximale | Maximale | Données envoyées à Google |
| RAM requise | ~5 GB | ~6 GB | ~6 GB | N/A |
| Latence | 5-15s | 5-15s | 5-15s | 1-2s |
| Multilingue | Oui | Oui | Excellent | Oui |

---

## Stratégies RAG

Toutes les stratégies héritent de `RAGStrategy` et implémentent `retrieve()` et `build_prompt()`.

### 1. Simple RAG — `simple_rag.py`

**Principe** : Recherche sémantique uniquement, retourne les k=5 documents les plus proches.

```
Question → Vecteur → ChromaDB (top 5) → Filtre accès → Prompt → LLM
```

**Usage** : Prototypage, tests rapides, cas simples.

### 2. Secure RAG — `secure_rag.py`

**Principe** : Identique au Simple RAG mais avec un refus explicite dans le prompt si l'utilisateur tente d'accéder à des informations non autorisées.

**Usage** : Production, contextes juridiques, données sensibles.

### 3. Hybrid RAG — `hybrid_rag.py`

**Principe** : Recherche sémantique large (k=10) + réordonnancement par score lexical (mots-clés). Retourne les 3 meilleurs après fusion des scores.

```
Question → ChromaDB (top 10) → Score lexical → Tri → Top 3 → LLM
```

**Usage** : Amélioration de la précision, réduction des faux positifs sémantiques.

### 4. Modular RAG — `modular_rag.py`

**Principe** : Architecture extensible pour expérimentations (query rewriting, multi-étapes, agents).

**Usage** : R&D, expérimentation de pipelines avancés.

### 5. Reranking RAG — `reranking_rag.py`

**Principe** : Récupère 2×k documents, les reclasse avec un Cross-Encoder (`ms-marco-MiniLM-L-6-v2`), retourne top-k.

```
Question → ChromaDB (2k docs) → Cross-Encoder scoring → Top k → LLM
```

**Usage** : Précision maximale, quand la pertinence est critique.

### Tableau comparatif

| Stratégie | Vitesse | Précision | Complexité | Recommandé pour |
|-----------|---------|-----------|------------|-----------------|
| Simple | Rapide | Moyenne | Faible | Tests, démos |
| Secure | Rapide | Moyenne | Faible | Production |
| Hybrid | Moyenne | Bonne | Moyenne | Amélioration qualité |
| Modular | Variable | Variable | Haute | R&D |
| Reranking | Lente | Excellente | Haute | Précision critique |

---

## Système de sécurité et contrôle d'accès

### Authentification

1. L'utilisateur entre son `username` + `password` dans Streamlit
2. `auth_service.py` vérifie les credentials contre MySQL (bcrypt)
3. Un token JWT est créé (expiration 1h) et stocké en session
4. À chaque requête, le JWT est décodé pour extraire le rôle

### Hiérarchie des accès

```
admin       → confidential (niveau 2) → accès à TOUT
employee    → internal     (niveau 1) → accès public + internal
guest       → public       (niveau 0) → accès public uniquement
```

### Règle d'autorisation — `search.py`

```python
def is_authorized(doc_access_level, user_access_level):
    return ACCESS_ORDER[user_access_level] >= ACCESS_ORDER[doc_access_level]
```

Un utilisateur accède à tous les documents dont le niveau est **inférieur ou égal** au sien.

### Classification automatique des documents — `prepare_corpus.py`

Les documents sont classifiés automatiquement lors de la préparation du corpus :

| Niveau | Mots-clés déclencheurs |
|--------|------------------------|
| `confidential` | payment, fee, price, penalty, damages, termination, liability, confidential, compensation, indemnity |
| `public` | definition, definitions, purpose, scope |
| `internal` | tout le reste |

### Comportement du pipeline selon l'accès

| Situation | Comportement |
|-----------|-------------|
| Documents autorisés trouvés | LLM répond avec le contexte des documents |
| Aucun document autorisé | LLM répond uniquement aux questions sur son rôle |
| Question hors rôle sans docs | Répond : "You do not have access to this type of information." |

---

## Base documentaire

### Source des données

Dataset **SECOP** (Système Électronique de Contrats Publics de Colombie) — contrats administratifs réels entre l'État colombien et des prestataires.

### Statistiques

| Métrique | Valeur |
|----------|--------|
| Nombre total de documents | 521 |
| Niveau `public` | 1 |
| Niveau `internal` | 518 |
| Niveau `confidential` | 2 |
| Taille minimale | 1 098 caractères |
| Taille maximale | 411 132 caractères |
| Taille moyenne | 35 907 caractères |
| Langue des contrats | Espagnol |

### Structure d'un document

```json
{
  "text": "texte complet du contrat...",
  "access_level": "public | internal | confidential",
  "source": "Contracts-SECOP-NER"
}
```

### Embeddings et indexation

- **Modèle d'embedding** : `sentence-transformers/all-MiniLM-L6-v2`
- **Base vectorielle** : ChromaDB (persistée dans `db/`)
- **Recherche** : similarité cosinus entre vecteur question et vecteurs documents

---

## Pipeline RAG — Fonctionnement détaillé

### Étape par étape

**1. Question posée par l'utilisateur**

**2. Conversion en vecteur**
Le modèle `all-MiniLM-L6-v2` transforme la question en vecteur numérique représentant son sens sémantique.

**3. Recherche dans ChromaDB**
ChromaDB compare le vecteur question avec les 521 vecteurs documents et retourne les k plus proches sémantiquement (pas par mots-clés, mais par sens).

**4. Filtrage par droits d'accès**
Chaque document retourné est vérifié : si `doc.access_level > user.access_level`, il est exclu.

**5a. Si documents autorisés trouvés**
```
Contexte = concaténation des textes des documents autorisés
Prompt = "Answer using context below: [contexte] Question: [question]"
Réponse = llm.generate(prompt)
```

**5b. Si aucun document autorisé**
```
Prompt = system_prompt (description du rôle de l'assistant) + question
Réponse = llm.generate(prompt)
→ Répond sur son rôle OU refuse poliment
```

**6. Affichage dans Streamlit**
Réponse + sources utilisées (expandables).

---

## Support Multi-LLM — Pattern Factory

### Principe

Tous les LLMs implémentent la même interface :

```python
# base.py
class LLM(ABC):
    def generate(self, prompt: str) -> str:
        ...
```

Le pipeline appelle uniquement `llm.generate(prompt)` sans savoir quel LLM est derrière.

### Factory

```python
# factory.py
def get_llm(name: str):
    if name == "mistral": return MistralLLM()
    if name == "llama":   return LlamaLLM()
    if name == "qwen":    return QwenLLM()
    if name == "gemini":  return GeminiLLM()
```

### Avantage

Ajouter un nouveau LLM = créer 1 fichier + ajouter 1 ligne dans `factory.py`. Le reste du code ne change pas.

---

## Installation et démarrage

### Prérequis

- Python 3.8+
- MySQL (via XAMPP ou autre)
- Ollama installé (pour les modèles locaux)
- 8 GB RAM minimum recommandés

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer l'environnement

Créer un fichier `.env` à la racine :

```bash
JWT_SECRET_KEY=<générer-une-clé-aléatoire>
GEMINI_API_KEY=AIza...   # Optionnel, seulement si vous utilisez Gemini
```

Générer une clé JWT :
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 3. Configurer la base de données MySQL

```bash
python scripts/setup_database.py
python scripts/seed_users.py
```

### 4. Indexer les documents

```bash
python src/ingestion.py
```

### 5. Télécharger les modèles Ollama

```bash
ollama pull mistral
ollama pull llama3.1:8b
ollama pull qwen3:8b
```

### 6. Lancer l'application

```bash
cd src
python -m streamlit run app.py
```

Accéder à : http://localhost:8501

---

## Utilisation

### Connexion

| Utilisateur | Mot de passe | Rôle | Accès |
|-------------|--------------|------|-------|
| `alice` | `alice123` | guest | public uniquement |
| `bob` | `bob123` | employee | public + internal |
| `admin` | `admin123` | admin | tout |

### Questions par niveau d'accès

**Guest (public)**
- "What are the general conditions of use of public services?"
- "What is your role?" *(répondu par le system prompt)*
- "What can you do?" *(répondu par le system prompt)*

**Employee (internal)**
- "What are the obligations of the parties in the contract?"
- "What is the scope of services in the contract?"
- "What are the general terms of the agreement?"

**Admin (confidential)**
- "What are the payment terms and fees?"
- "What are the penalties in case of late payment?"
- "What are the liability clauses?"

### Sélection LLM × RAG

Dans la sidebar Streamlit :
- **Language Model** : `mistral`, `qwen`, `llama`, `gemini`
- **RAG Strategy** : `simple`, `secure`, `hybrid`, `modular`

Toutes les combinaisons sont possibles sans modification du code.

---

## Gestion des utilisateurs

### Ajouter un utilisateur

```bash
python scripts/add_user.py
```

Ou en ligne de commande :
```bash
python scripts/add_user.py charlie charlie123 employee charlie@company.com
```

### Modifier un rôle (MySQL)

```sql
UPDATE users SET role = 'admin' WHERE username = 'bob';
```

### Désactiver un utilisateur

```sql
UPDATE users SET is_active = FALSE WHERE username = 'alice';
```

---

## Ajouter un LLM ou une stratégie RAG

### Ajouter un nouveau LLM

1. Créer `src/llms/mon_llm.py` :
```python
from .base import LLM

class MonLLM(LLM):
    def generate(self, prompt: str) -> str:
        # Votre implémentation
        return "réponse"
```

2. Ajouter dans `src/factory.py` :
```python
from llms.mon_llm import MonLLM

def get_llm(name: str):
    if name == "monllm": return MonLLM()
    ...
```

3. Ajouter dans `src/app.py` le selectbox :
```python
["mistral", "qwen", "llama", "gemini", "monllm"]
```

### Ajouter une stratégie RAG

1. Créer `src/rag_strategies/ma_strategie.py` héritant de `RAGStrategy`
2. Implémenter `retrieve()` et `build_prompt()`
3. Enregistrer dans `factory.py` et `app.py`

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Interface | Streamlit |
| Base vectorielle | ChromaDB |
| Embeddings | HuggingFace Sentence Transformers (all-MiniLM-L6-v2) |
| Reranking | Cross-Encoder (ms-marco-MiniLM-L-6-v2) |
| LLMs locaux | Ollama (Mistral, Llama, Qwen) |
| LLM cloud | Google Gemini API |
| Authentification | PyJWT + MySQL + bcrypt |
| Évaluation | MRR, NDCG@k, Precision@k, F1 sémantique |
| Visualisation | Plotly + Pandas |

---

## Licence

Projet développé dans un cadre R&D académique .
