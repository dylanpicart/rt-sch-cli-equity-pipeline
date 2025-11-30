from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from .config import get_settings

settings = get_settings()

client = chromadb.Client(
    ChromaSettings(
        persist_directory=settings.VECTOR_DIR,
    )
)

_COLLECTION_NAME = "school_climate_semantic"

def get_collection():
    return client.get_or_create_collection(_COLLECTION_NAME)

def upsert_documents(
    ids: List[str],
    texts: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict[str, Any]],
):
    col = get_collection()
    col.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

def query_similar(
    query_embedding: List[float],
    k: int = 8,
) -> List[Dict[str, Any]]:
    col = get_collection()
    result = col.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )
    # Normalize output
    hits = []
    for i, doc in enumerate(result["documents"][0]):
        hits.append(
            {
                "id": result["ids"][0][i],
                "text": doc,
                "metadata": result["metadatas"][0][i],
                "distance": result["distances"][0][i],
            }
        )
    return hits
