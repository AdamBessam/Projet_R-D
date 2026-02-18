# Secure RAG Legal Project

Projet R&D de système Retrieval-Augmented Generation (RAG) sécurisé pour répondre à des questions sur des documents contractuels juridiques, avec contrôle d'accès par rôles et support de multiples modèles LLM.

---

## 🚀 Démarrage Rapide

**Nouveau sur ce projet ?** Suivez le guide d'installation complet : **[INSTALLATION.md](INSTALLATION.md)**

### Installation en 5 minutes

```bash
# 1. Cloner et installer
git clone <URL_DU_REPO>
cd rag_legal_project
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configurer MySQL (XAMPP)
# → Démarrer MySQL dans XAMPP Control Panel
python scripts/setup_database.py
python scripts/seed_users.py

# 3. Lancer l'application
streamlit run src/app.py
```

**Test rapide** : Connectez-vous avec `admin` / `admin123` sur http://localhost:8501

📖 **Guide complet** : [INSTALLATION.md](INSTALLATION.md)

---

## 📋 Table des matières

- [Démarrage Rapide](#-démarrage-rapide)
- [Contexte du projet](#contexte-du-projet)
- [Architecture](#architecture)
- [Comparatif des modèles LLM](#comparatif-des-modèles-llm)
- [Comparatif des stratégies RAG](#comparatif-des-stratégies-rag)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Tests](#tests)
- [Sécurité](#sécurité)
- [Gestion des Utilisateurs](#gestion-des-utilisateurs)

## 🎯 Contexte du projet

Ce projet répond à la problématique de recherche et d'analyse dans des bases documentaires juridiques avec des contraintes de sécurité et de confidentialité. Il combine :

- **Modèles de langage à grande échelle (LLM)** : pour générer des réponses en langage naturel
- **Retrieval-Augmented Generation (RAG)** : pour ancrer les réponses dans des documents factuels
- **Contrôle d'accès granulaire** : pour respecter les droits d'accès selon les utilisateurs

### Fonctionnalités principales

- ✅ Ingestion et préparation de corpus de clauses contractuelles
- ✅ Création d'embeddings et indexation vectorielle (ChromaDB)
- ✅ Recherche sémantique avec filtrage par niveau d'accès
- ✅ 4 stratégies RAG modulaires (simple, secure, hybrid, modular)
- ✅ Support de 3 LLM providers (OpenAI, Ollama local, Gemini)
- ✅ Interface utilisateur Streamlit avec authentification JWT
- ✅ Tests unitaires et configuration de sécurité

## 🏗️ Architecture

```
┌─────────────────┐
│  UI Streamlit   │ ← Authentification JWT
└────────┬────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Pipeline RAG (pipeline.py)     │
    └────┬─────────────────────┬───────┘
         │                     │
    ┌────▼──────────┐    ┌────▼────────┐
    │ RAG Strategy  │    │  LLM Adapter│
    │ (4 variants)  │    │ (3 providers)│
    └────┬──────────┘    └─────────────┘
         │
    ┌────▼────────────────┐
    │  Search + Security  │ ← Filtrage ACL
    └────┬────────────────┘
         │
    ┌────▼────────┐
    │  ChromaDB   │ ← Base vectorielle
    └─────────────┘
```

### Structure du projet

```
rag_legal_project/
├── src/
│   ├── app.py                  # Interface Streamlit
│   ├── pipeline.py             # Orchestration RAG
│   ├── search.py               # Recherche sécurisée
│   ├── ingestion.py            # Indexation documents
│   ├── prepare_corpus.py       # Préparation corpus
│   ├── auth.py / auth_service.py / security.py  # Authentification
│   ├── llms/                   # Adaptateurs LLM
│   │   ├── base.py
│   │   ├── openai_llm.py
│   │   ├── ollama_llm.py
│   │   └── gemini_llm.py
│   └── rag_strategies/         # Stratégies RAG
│       ├── simple_rag.py
│       ├── secure_rag.py
│       ├── hybrid_rag.py
│       └── modular_rag.py
├── data/
│   ├── contracts.jsonl         # Corpus brut
│   └── contracts_with_access.jsonl  # Corpus avec ACL
├── db/                         # Base vectorielle ChromaDB
├── tests/                      # Tests unitaires
└── scripts/                    # Scripts utilitaires
```

## 🤖 Comparatif des modèles LLM

### Tableau comparatif

| Critère | OpenAI (GPT-4o-mini) | Ollama (Mistral local) | Gemini (2.5-flash) |
|---------|---------------------|------------------------|-------------------|
| **Coût** | ~0.15$/1M tokens (entrée) | Gratuit (auto-hébergé) | Gratuit (API quota) |
| **Latence** | 1-3s (API externe) | 5-15s (local, dépend CPU/RAM) | 1-2s (API externe) |
| **Qualité réponse** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Très bon | ⭐⭐⭐⭐⭐ Excellent |
| **Confidentialité** | ⚠️ Données envoyées à OpenAI | ✅ 100% local | ⚠️ Données envoyées à Google |
| **Limite contexte** | 128K tokens | 4K-32K (selon modèle) | 1M tokens |
| **RAM requise** | N/A (API) | 4-8 GB minimum | N/A (API) |
| **Scalabilité** | ✅ Élastique | ⚠️ Limitée par hardware | ✅ Élastique |
| **Maintenance** | ✅ Gérée par OpenAI | ⚠️ Mises à jour manuelles | ✅ Gérée par Google |

### Recommandations d'usage

**OpenAI GPT-4o-mini** 
- ✅ Production avec budget
- ✅ Qualité maximale requise
- ❌ Données ultra-sensibles

**Ollama (Mistral)**
- ✅ Développement/test
- ✅ Confidentialité maximale
- ✅ Pas de coûts récurrents
- ❌ Infrastructure limitée

**Gemini 2.5-flash**
- ✅ Prototypage rapide
- ✅ Contextes très longs
- ✅ Quota gratuit généreux
- ❌ Dépendance à Google

### Implémentation dans le projet

Tous les LLM sont abstraits via l'interface `LLM` ([src/llms/base.py](src/llms/base.py)) permettant de changer de provider sans modifier le code métier :

```python
# Factory pattern pour sélection dynamique
llm = get_llm("openai")  # ou "ollama" ou "gemini"
answer = llm.generate(prompt)
```

## 🔍 Comparatif des stratégies RAG

### Tableau comparatif

| Stratégie | Complexité | Performance | Sécurité | Cas d'usage |
|-----------|-----------|-------------|----------|-------------|
| **Simple RAG** | ⭐ Basique | ⭐⭐⭐ Rapide | ⭐⭐ Standard | Prototypage, démos |
| **Secure RAG** | ⭐⭐ Moyenne | ⭐⭐⭐ Rapide | ⭐⭐⭐⭐⭐ Maximum | Production juridique/santé |
| **Hybrid RAG** | ⭐⭐⭐ Avancée | ⭐⭐⭐⭐ Optimisée | ⭐⭐⭐ Renforcée | Amélioration précision |
| **Modular RAG** | ⭐⭐⭐⭐ Complexe | ⭐⭐⭐⭐ Configurable | ⭐⭐⭐⭐ Extensible | R&D, expérimentation |

### Détail des stratégies

#### 1. Simple RAG ([simple_rag.py](src/rag_strategies/simple_rag.py))

**Principe** : Recherche sémantique basique (top-k=3) avec filtrage ACL minimal.

**Avantages** :
- Simplicité d'implémentation
- Latence minimale
- Facile à débugger

**Limites** :
- Pas de réordonnancement
- Peut manquer des documents pertinents

#### 2. Secure RAG ([secure_rag.py](src/rag_strategies/secure_rag.py))

**Principe** : Filtrage strict par niveau d'accès + refus explicite si aucun document autorisé.

**Avantages** :
- ✅ Garantie de conformité (pas de réponse sans source autorisée)
- ✅ Traçabilité complète des sources
- ✅ Prompt explicite sur les limites

**Limites** :
- Peut refuser des requêtes légitimes si ACL trop restrictive

**Code clé** :
```python
documents = secure_search(query, user_access_level, k=5)
if not documents:
    return []  # Refus explicite
```

#### 3. Hybrid RAG ([hybrid_rag.py](src/rag_strategies/hybrid_rag.py))

**Principe** : Recherche sémantique large (k=10) + réordonnancement lexical (keyword matching).

**Avantages** :
- ✅ Meilleure précision (combine sémantique + mots-clés)
- ✅ Réduit les faux positifs sémantiques
- ✅ Top-3 final après réordonnancement

**Processus** :
1. Recherche sémantique → 10 candidats
2. Score lexical par mot-clé
3. Tri par score → top-3

#### 4. Modular RAG ([modular_rag.py](src/rag_strategies/modular_rag.py))

**Principe** : Architecture extensible pour query rewriting, multi-étapes, agents.

**Caractéristiques** :
- Recherche large (k=8) avec filtrage à 3
- Placeholder pour étapes futures :
  - Query expansion
  - Re-ranking par modèle
  - Vérification croisée

**Usage** : Base pour expérimentations avancées (agentic RAG, chain-of-thought retrieval).

### Sélection de la stratégie

Dans l'interface Streamlit, l'utilisateur peut choisir dynamiquement :

```python
rag = get_rag_strategy("secure")  # ou "simple", "hybrid", "modular"
```

**Recommandation** : `secure` pour production juridique, `hybrid` pour meilleure précision, `simple` pour tests rapides.

## 📦 Installation

### Prérequis

- Python 3.8+
- 4 GB RAM minimum (8 GB recommandé si usage Ollama)

### Étapes

1. **Cloner le projet** :
```powershell
git clone <url-du-projet>
cd rag_legal_project
```

2. **Créer un environnement virtuel** (Windows PowerShell) :
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Installer les dépendances** :
```powershell
pip install -r requirements.txt
```

## ⚙️ Configuration

### Variables d'environnement requises

Créer un fichier `.env` à la racine :

```bash
# OBLIGATOIRE
JWT_SECRET_KEY=<générer-une-clé-sécurisée>

# Optionnel selon le LLM utilisé
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```

**Générer une clé JWT sécurisée** :
```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Utilisateurs par défaut

Définis dans [src/users.py](src/users.py) :

| Utilisateur | Mot de passe | Rôle | Niveau d'accès |
|-------------|--------------|------|----------------|
| `alice` | `alice123` | guest | `public` |
| `bob` | `bob123` | employee | `internal` |
| `admin` | `admin123` | admin | `confidential` |

## 🚀 Utilisation

### 1. Préparer le corpus

Si vous avez des contrats bruts dans `data/contracts.jsonl` :

```powershell
python src/prepare_corpus.py
```

Cela génère `data/contracts_with_access.jsonl` avec classification automatique des niveaux d'accès.

### 2. Indexer les documents

```powershell
python src/ingestion.py
```

Crée les embeddings et peuple ChromaDB dans `db/`.

### 3. Lancer l'interface

```powershell
$env:JWT_SECRET_KEY = '<votre-clé>'
streamlit run src/app.py
```

Accéder à http://localhost:8501

### 4. Tester

1. **Login** : Utiliser `admin` / `admin123` pour accès complet
2. **Sélectionner** :
   - Stratégie RAG : `secure` (recommandé)
   - LLM : `gemini` (gratuit) ou `openai` (si clé API)
3. **Poser une question** : 
   - Public : "Quelle est la définition de..." 
   - Confidentiel : "Quelles sont les pénalités de résiliation..."

## 🧪 Tests

Exécuter les tests unitaires :

```powershell
python -m pytest -q
```

Tests disponibles :
- `tests/test_search.py` : Vérification de la logique ACL
- `tests/test_rag.py` : Validation de la génération de prompts

Pour ajouter des tests :
```python
# tests/test_custom.py
def test_custom_logic():
    # Votre test
    assert True
```

## 🔒 Sécurité

### Authentification

- **JWT** avec expiration (1h par défaut)
- **Mots de passe** : Support bcrypt (utiliser `scripts/hash_password.py` pour migration)
- **Variables sensibles** : `.env` (ne jamais commit dans Git)

### Contrôle d'accès

Hiérarchie des niveaux :
```
confidential (2) > internal (1) > public (0)
```

Règle : Un utilisateur `internal` accède à `internal` + `public`, mais pas `confidential`.

Implémentation : [src/search.py](src/search.py#L23-L29)

### Recommandations production

❌ **Ne pas faire** :
- Stocker mots de passe en clair
- Exposer `.env` ou `JWT_SECRET_KEY`
- Utiliser valeurs par défaut en production

✅ **À faire** :
- Intégrer LDAP/IdP (Active Directory, Okta)
- Utiliser secrets manager (Azure KeyVault, AWS Secrets)
- Activer HTTPS
- Logger les accès (audit trail)
- Rate limiting sur API LLM

## 📊 Performance

### Benchmarks indicatifs (CPU i7, 16GB RAM)

| Métrique | Simple RAG | Secure RAG | Hybrid RAG |
|----------|-----------|-----------|-----------|
| Recherche (ms) | 150 | 180 | 250 |
| Génération LLM (s) | 1-3 | 1-3 | 1-3 |
| **Total (s)** | **1.5-3.5** | **1.5-3.5** | **1.5-3.5** |

*Temps de génération dépend fortement du LLM choisi et de la longueur du prompt.*

---

## 👥 Gestion des Utilisateurs

### Utilisateurs par Défaut

Après l'installation, 3 comptes sont créés automatiquement :

| Utilisateur | Mot de passe | Rôle | Niveau d'accès | Accès aux documents |
|-------------|--------------|------|----------------|---------------------|
| **alice** | alice123 | guest | public | ✅ Public uniquement |
| **bob** | bob123 | employee | internal | ✅ Public + Internal |
| **admin** | admin123 | admin | confidential | ✅ Tous (Public + Internal + Confidential) |

### Ajouter un Nouvel Utilisateur

#### **Option 1 : Mode Interactif (Recommandé)**

```bash
python scripts/add_user.py
```

Le script vous guidera étape par étape :
```
🔐 AJOUT D'UN NOUVEL UTILISATEUR
👤 Nom d'utilisateur: charlie
🔑 Mot de passe: charlie123
👥 Choisir un rôle (1-3): 2
📧 Email: charlie@company.com
✅ Utilisateur 'charlie' créé avec succès !
```

#### **Option 2 : Mode Ligne de Commande**

```bash
python scripts/add_user.py <username> <password> <role> [email]
```

**Exemple** :
```bash
python scripts/add_user.py charlie charlie123 employee charlie@company.com
```

#### **Option 3 : Programmatiquement**

```python
from scripts.add_user import add_user

add_user("david", "david123", "admin", "david@company.com")
```

### Rôles et Permissions

| Rôle | Niveau d'accès | Cas d'usage |
|------|----------------|-------------|
| **guest** | `public` | Utilisateurs externes, invités, consultants |
| **employee** | `internal` | Employés de l'entreprise, utilisateurs standards |
| **admin** | `confidential` | Managers, direction, juristes habilités |

### Modifier un Utilisateur Existant

#### **Changer le mot de passe**

Via MySQL/phpMyAdmin :
```sql
UPDATE users 
SET password_hash = '$2b$12$...'  -- Utiliser bcrypt pour hasher
WHERE username = 'bob';
```

⚠️ **Important** : Le mot de passe doit être hashé avec bcrypt !

#### **Changer le rôle**

```sql
UPDATE users 
SET role = 'admin' 
WHERE username = 'bob';
```

#### **Désactiver un utilisateur**

```sql
UPDATE users 
SET is_active = FALSE 
WHERE username = 'alice';
```

### Lister Tous les Utilisateurs

```bash
python scripts/check_mysql_setup.py
```

Ou via MySQL :
```sql
SELECT id, username, role, email, is_active, last_login 
FROM users 
ORDER BY id;
```

### Supprimer un Utilisateur

```sql
DELETE FROM users WHERE username = 'charlie';
```

⚠️ **Attention** : Cette action est irréversible !

---

## 🛠️ Développement

### Ajouter un nouveau LLM

1. Créer `src/llms/my_llm.py` :
```python
from .base import LLM

class MyLLM(LLM):
    def generate(self, prompt: str) -> str:
        # Votre implémentation
        pass
```

2. Enregistrer dans `src/factory.py` :
```python
def get_llm(name: str):
    if name == "myllm":
        return MyLLM()
    # ...
```

### Ajouter une stratégie RAG

1. Créer `src/rag_strategies/my_rag.py` héritant de `RAGStrategy`
2. Implémenter `retrieve()` et `build_prompt()`
3. Enregistrer dans `factory.py`

## 📝 Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout fonctionnalité X'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est développé dans un cadre R&D académique.

## 🙏 Remerciements

- **LangChain** : Framework RAG
- **ChromaDB** : Base vectorielle
- **Sentence Transformers** : Embeddings
- **Streamlit** : Interface utilisateur
