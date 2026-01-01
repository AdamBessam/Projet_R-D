import json
import re
from tqdm import tqdm

INPUT_PATH = "data/contracts.jsonl"
OUTPUT_PATH = "data/contracts_with_access.jsonl"

def assign_access_level(text: str) -> str:
    """
    Attribue un niveau d'accès à une clause contractuelle
    selon des règles heuristiques simples.
    """

    text_lower = text.lower()

    confidential_keywords = [
        "payment", "fee", "price", "penalty", "damages",
        "termination", "liability", "confidential",
        "compensation", "indemnity"
    ]

    public_keywords = [
        "definition", "definitions", "purpose", "scope"
    ]

    for kw in confidential_keywords:
        if kw in text_lower:
            return "confidential"

    for kw in public_keywords:
        if kw in text_lower:
            return "public"

    return "internal"


def clean_text(text: str) -> str:
    """
    Nettoyage minimal du texte juridique
    (suppression espaces multiples, lignes vides).
    """
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def prepare_corpus():
    processed = 0

    with open(INPUT_PATH, "r", encoding="utf-8") as fin, \
         open(OUTPUT_PATH, "w", encoding="utf-8") as fout:

        for line in tqdm(fin, desc="Processing contracts"):
            data = json.loads(line)

            if "text" not in data:
                continue

            text = clean_text(data["text"])

            if len(text) < 50:
                continue  # ignore clauses trop courtes

            access_level = assign_access_level(text)

            document = {
                "text": text,
                "access_level": access_level,
                "source": "Contracts-SECOP-NER"
            }

            fout.write(json.dumps(document, ensure_ascii=False) + "\n")
            processed += 1

    print(f"✔ Corpus préparé : {processed} clauses enregistrées")
    print(f"✔ Fichier généré : {OUTPUT_PATH}")


if __name__ == "__main__":
    prepare_corpus()
