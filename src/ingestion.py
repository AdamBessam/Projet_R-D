import json
from tqdm import tqdm
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


INPUT_PATH = "data/contracts_with_access.jsonl"
DB_PATH = "db"

def load_documents():
    documents = []

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Loading documents"):
            data = json.loads(line)

            doc = Document(
                page_content=data["text"],
                metadata={
                    "access_level": data["access_level"],
                    "source": data["source"]
                }
            )
            documents.append(doc)

    return documents


def ingest():
    print("▶ Chargement des documents...")
    documents = load_documents()

    print("▶ Création des embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("▶ Indexation dans ChromaDB...")
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    vectordb.persist()
    print(f"✔ Indexation terminée : {len(documents)} documents indexés")


if __name__ == "__main__":
    ingest()
