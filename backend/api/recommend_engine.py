"""
recommend_engine.py  -  MODEL 1: Sentence Transformer + Vector Similarity Search
==================================================================================

Data flow:

    77 Indian Standards (bis_data.json)
            |
            v
    Sentence Transformer (all-MiniLM-L6-v2)   <- PRETRAINED, not fine-tuned here
            |  encodes "Title: ... Scope: ..." for each standard
            v
    Dense embeddings stored in a persistent vector index (ChromaDB)
            |
    User query
            |
    Sentence Transformer embeds the query with the SAME pretrained model
            |
            v
    Vector similarity search (cosine/L2 over the stored embeddings)
            |
            v
    Ranked standards -> top-N recommendations

IMPORTANT - PRETRAINED, NOT TRAINED ON THESE 77 STANDARDS:
all-MiniLM-L6-v2 is a general-purpose sentence embedding model trained by
its original authors on large public sentence-pair corpora. The 77
standards are NOT training data for it - they are simply passed through
the frozen, pretrained model to get embeddings, which are then indexed
and searched. No fine-tuning happens in this file.

IMPORTANT - "FAISS" NAMING NOTE:
This engine uses ChromaDB's built-in vector index (HNSW-based approximate
nearest neighbour search), not a literal `faiss.IndexFlatIP` index. The
retrieval CONCEPT is the same (embed -> nearest-neighbour search -> rank),
but the underlying library is Chroma, not FAISS. This is stated plainly
here and in ARCHITECTURE.md so the model comparison stays accurate.
"""

import json
import os
import chromadb
from chromadb.utils import embedding_functions

MODEL_NAME = "Sentence Transformer (all-MiniLM-L6-v2) + Vector Similarity Search (ChromaDB)"

_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_HERE, "bis_data.json")
DB_PATH = os.path.join(_HERE, "bis_vector_db")
COLLECTION_NAME = "indian_standards"

# Initialize persistent vector DB
chroma_client = chromadb.PersistentClient(path=DB_PATH)

# Use local open-source embedding model (PRETRAINED, frozen - no fine-tuning)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME, embedding_function=sentence_transformer_ef
)


def _load_standards(json_file_path=None):
    path = json_file_path or DATA_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def populate_database(json_file_path=None):
    """Loads the shared 77-standard JSON into the vector database.

    Idempotent: if the collection already holds exactly as many vectors
    as there are standards, it is left untouched. If the dataset has
    changed size since the last run (e.g. you edited bis_data.json),
    the collection is rebuilt from scratch so the index never goes stale.
    """
    global collection

    standards = _load_standards(json_file_path)

    if collection.count() == len(standards):
        return  # already correctly seeded

    if collection.count() != 0:
        # Dataset changed since the index was built - rebuild cleanly.
        chroma_client.delete_collection(COLLECTION_NAME)
        collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME, embedding_function=sentence_transformer_ef
        )

    documents = []
    metadatas = []
    ids = []

    for item in standards:
        # Context-rich text used for the embedding (same text basis used
        # by Model 2's BiLSTM encoder, so both models see equivalent input).
        rich_text = f"Title: {item['title']}. Scope: {item['scope']}."
        documents.append(rich_text)

        metadatas.append(
            {
                "is_code": item["is_code"],
                "title": item["title"],
                "allied_standards": ",".join(item["allied_standards"]),
                "test_methods": ",".join(item["test_methods"]),
                "mandatory_cert": str(item["mandatory_cert"]),
                "scheme": item["scheme"],
                "status": item["status"],
            }
        )
        ids.append(item["is_code"])

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Vector database populated with {len(standards)} standards.")


def recommend_standards(query_text: str, n_results: int = 5):
    """Embeds the query with the SAME pretrained Sentence Transformer used
    to index the standards, then performs a nearest-neighbour vector
    search to retrieve and rank the most similar standards."""
    results = collection.query(query_texts=[query_text], n_results=n_results)

    recommendations = []
    for rank, (meta, dist) in enumerate(
        zip(results["metadatas"][0], results["distances"][0]), start=1
    ):
        recommendations.append(
            {
                "is_code": meta["is_code"],
                "title": meta["title"],
                "allied_standards": meta["allied_standards"].split(",") if meta["allied_standards"] else [],
                "test_methods": meta["test_methods"].split(",") if meta["test_methods"] else [],
                "mandatory_cert": meta["mandatory_cert"] == "True",
                "scheme": meta["scheme"],
                "status": meta["status"],
                "relevance_score": round((1 - dist) * 100, 2),  # distance -> similarity %
                "rank": rank,
            }
        )
    return recommendations


# Seed DB when script runs directly
if __name__ == "__main__":
    populate_database()
    results = recommend_standards(
        "Procurement of thermo-mechanically treated steel rods for bridges"
    )
    print(json.dumps(results, indent=2))
