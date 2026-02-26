# import json
# from tqdm import tqdm
# from langchain_core.documents import Document
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma


# INPUT_PATH = "data/contracts_with_access.jsonl"
# DB_PATH = "db"

# def load_documents():
#     documents = []

#     with open(INPUT_PATH, "r", encoding="utf-8") as f:
#         for line in tqdm(f, desc="Loading documents"):
#             data = json.loads(line)

#             doc = Document(
#                 page_content=data["text"],
#                 metadata={
#                     "access_level": data["access_level"],
#                     "source": data["source"]
#                 }
#             )
#             documents.append(doc)

#     return documents


# def ingest():
#     print("▶ Chargement des documents...")
#     documents = load_documents()

#     print("▶ Création des embeddings...")
#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2"
#     )

#     print("▶ Indexation dans ChromaDB...")
#     vectordb = Chroma.from_documents(
#         documents=documents,
#         embedding=embeddings,
#         persist_directory=DB_PATH
#     )

#     vectordb.persist()
#     print(f"✔ Indexation terminée : {len(documents)} documents indexés")


# if __name__ == "__main__":
#     ingest()


import json
import os
from tqdm import tqdm
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings  # ← ancien import
from langchain_community.vectorstores import Chroma

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────

INPUT_PATH = "data/contracts_with_access.jsonl"
DB_PATH    = "db"

# Modèle multilingue — supporte ES, FR, EN et 50+ autres langues
# Remplace "all-MiniLM-L6-v2" qui était anglais uniquement
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Niveaux d'accès valides dans ta base documentaire
VALID_ACCESS_LEVELS = {"public", "internal", "confidential", "restricted"}


# ─────────────────────────────────────────
# CHARGEMENT DES DOCUMENTS
# ─────────────────────────────────────────

def load_documents(input_path: str) -> list[Document]:
    """
    Lit le fichier JSONL et crée les objets Document LangChain.
    Chaque ligne doit contenir : text, access_level, source.

    Exemple de ligne :
    {"text": "CONTRATO DE ...", "access_level": "internal", "source": "Contracts-SECOP-NER"}
    """
    documents = []
    skipped   = 0

    with open(input_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(tqdm(f, desc="Chargement des documents"), start=1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  ⚠ Ligne {i} ignorée (JSON invalide) : {e}")
                skipped += 1
                continue

            # Vérification des champs obligatoires
            if "text" not in data or not data["text"].strip():
                print(f"  ⚠ Ligne {i} ignorée (champ 'text' vide ou absent)")
                skipped += 1
                continue

            # Normalisation du niveau d'accès
            access_level = data.get("access_level", "public").lower().strip()
            if access_level not in VALID_ACCESS_LEVELS:
                print(f"  ⚠ Ligne {i} : niveau d'accès inconnu '{access_level}' → forcé à 'internal'")
                access_level = "internal"

            doc = Document(
                page_content=data["text"],
                metadata={
                    "access_level": access_level,
                    "source":       data.get("source", "unknown"),
                    "doc_index":    i,           # utile pour le debug
                    "language":     "es",        # les documents sont en espagnol
                }
            )
            documents.append(doc)

    print(f"\n  → {len(documents)} documents chargés, {skipped} ignorés")
    return documents


# ─────────────────────────────────────────
# CRÉATION DU MODÈLE D'EMBEDDING
# ─────────────────────────────────────────

def build_embeddings() -> HuggingFaceEmbeddings:
    """
    Initialise le modèle d'embedding multilingue.

    Pourquoi ce modèle ?
    - "all-MiniLM-L6-v2"  → anglais uniquement ❌
    - "paraphrase-multilingual-mpnet-base-v2" → ES + FR + EN + 50 langues ✅

    Conséquence : une query en français ou anglais trouvera
    correctement des documents en espagnol.
    """
    print(f"  Modèle : {EMBEDDING_MODEL}")
    print("  (Premier lancement = téléchargement ~420MB, patiente...)")

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"   # remplace par "cuda" si tu as un GPU
        },
        encode_kwargs={
            # Normalisation L2 — indispensable pour la similarité cosine
            # Sans ça, les scores de similarité sont faux
            "normalize_embeddings": True
        }
    )


# ─────────────────────────────────────────
# INDEXATION DANS CHROMADB
# ─────────────────────────────────────────

def build_vectorstore(
    documents: list[Document],
    embeddings: HuggingFaceEmbeddings,
    db_path: str
) -> Chroma:
    """
    Crée ou recrée la base vectorielle ChromaDB.
    Supprime l'ancienne base si elle existe pour éviter
    des conflits de modèles d'embedding.
    """

    # Nettoyage de l'ancienne base si elle existe
    if os.path.exists(db_path):
        print(f"  ⚠ Base existante détectée dans '{db_path}'")
        print("  → Suppression et recréation (modèle d'embedding changé)")
        import shutil
        shutil.rmtree(db_path)

    print(f"  Indexation de {len(documents)} documents...")
    print("  (Cette étape peut prendre plusieurs minutes)")

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=db_path,

        # Métadonnées de la collection pour traçabilité
        collection_metadata={
            "embedding_model": EMBEDDING_MODEL,
            "document_language": "es",
            "query_languages": "es,fr,en",
            "hnsw:space": "cosine"   # force la distance cosine
        }
    )

    vectordb.persist()
    return vectordb


# ─────────────────────────────────────────
# STATISTIQUES
# ─────────────────────────────────────────

def print_stats(documents: list[Document]) -> None:
    """
    Affiche un résumé de ce qui a été indexé.
    Utile pour vérifier que les droits d'accès sont bien répartis.
    """
    from collections import Counter

    access_counts = Counter(doc.metadata["access_level"] for doc in documents)
    source_counts  = Counter(doc.metadata["source"] for doc in documents)

    print("\n📊 Répartition par niveau d'accès :")
    for level, count in sorted(access_counts.items()):
        bar = "█" * (count // max(1, len(documents) // 20))
        print(f"   {level:15} : {count:4} docs  {bar}")

    print("\n📁 Répartition par source :")
    for source, count in source_counts.most_common(10):
        print(f"   {source:30} : {count:4} docs")


# ─────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────

def ingest() -> None:

    print("=" * 55)
    print("   INDEXATION RAG — Documents espagnols")
    print("   Requêtes supportées : ES / FR / EN")
    print("=" * 55)

    # Étape 1 — Chargement
    print("\n[1/3] Chargement des documents...")
    documents = load_documents(INPUT_PATH)

    if not documents:
        print("❌ Aucun document chargé. Vérifie le fichier source.")
        return

    print_stats(documents)

    # Étape 2 — Embeddings
    print("\n[2/3] Initialisation du modèle d'embedding multilingue...")
    embeddings = build_embeddings()

    # Étape 3 — Indexation
    print("\n[3/3] Indexation dans ChromaDB...")
    vectordb = build_vectorstore(documents, embeddings, DB_PATH)

    # Résumé final
    print("\n" + "=" * 55)
    print(f"✅ Indexation terminée !")
    print(f"   Documents indexés : {len(documents)}")
    print(f"   Base vectorielle  : {DB_PATH}/")
    print(f"   Modèle embedding  : {EMBEDDING_MODEL}")
    print(f"   Langues requêtes  : ES, FR, EN")
    print("=" * 55)
    print("\n⚠  Important : utilise le même modèle dans search.py !")
    print(f"   EMBEDDING_MODEL = \"{EMBEDDING_MODEL}\"")


if __name__ == "__main__":
    ingest()