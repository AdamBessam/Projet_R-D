from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

DB_PATH = "db"

# hiérarchie des niveaux d'accès
ACCESS_ORDER = {
    "public": 0,
    "internal": 1,
    "confidential": 2
}


def load_vectordb():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )
    return vectordb


def is_authorized(doc_access_level, user_access_level):
    """
    Vérifie si un utilisateur peut accéder à un document.
    """
    return ACCESS_ORDER[user_access_level] >= ACCESS_ORDER[doc_access_level]


def secure_search(query, user_access_level, k=5):
    """
    Recherche sémantique avec filtrage par droits d'accès.
    """
    vectordb = load_vectordb()

    # Recherche sémantique
    results = vectordb.similarity_search(query, k=k)

    # Filtrage sécurité
    authorized_docs = [
        doc for doc in results
        if is_authorized(doc.metadata["access_level"], user_access_level)
    ]

    return authorized_docs
