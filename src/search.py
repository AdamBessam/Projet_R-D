from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

DB_PATH = "db"

# Hiérarchie des niveaux d'accès
ACCESS_ORDER = {
    "public": 0,
    "internal": 1,
    "confidential": 2
}

# Chargement unique du modèle d'embeddings
_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Chargement unique de la base vectorielle
_vectordb = Chroma(
    persist_directory=DB_PATH,
    embedding_function=_embeddings
)


def is_authorized(doc_access_level: str, user_access_level: str) -> bool:
    """
    Vérifie si un utilisateur peut accéder à un document
    selon la hiérarchie des droits.
    """
    return ACCESS_ORDER.get(user_access_level, 0) >= ACCESS_ORDER.get(doc_access_level, 0)


def secure_search(query: str, user_access_level: str, k: int = 5):
    results = _vectordb.similarity_search(query, k=k)

    print("USER ACCESS:", user_access_level)
    print("RAW RESULTS:", len(results))

    for doc in results:
        print("DOC METADATA:", doc.metadata)

    authorized_docs = []

    for doc in results:
        doc_access_level = doc.metadata.get("access_level", "public")
        if is_authorized(doc_access_level, user_access_level):
            authorized_docs.append(doc)

    print("AUTHORIZED DOCS:", len(authorized_docs))
    return authorized_docs
