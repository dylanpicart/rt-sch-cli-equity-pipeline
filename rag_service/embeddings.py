from functools import lru_cache
from typing import List, Any

import math
import hashlib

from langchain_openai import OpenAIEmbeddings

from .config import get_settings

settings = get_settings()


class FakeEmbeddings:
    """
    Simple deterministic embedding implementation for dev/testing.

    - Does NOT call any external APIs.
    - Produces fixed-size vectors from the hash of the input text.
    - Obviously not semantically meaningful, but good enough to exercise
      the RAG stack (ingestion, retrieval, API, UI).
    """

    def __init__(self, dim: int = 64):
        self.dim = dim

    def _embed_single(self, text: str) -> List[float]:
        # Hash the text and turn it into a stable pseudo-random vector.
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Repeat the hash to reach desired dimension
        bytes_needed = self.dim
        buf = (h * ((bytes_needed // len(h)) + 1))[:bytes_needed]
        # Map bytes [0,255] to floats in [-1,1]
        vec = [((b / 255.0) * 2.0 - 1.0) for b in buf]
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_single(text)


@lru_cache
def _get_embedding_client() -> Any:
    """
    Return the embedding client according to configuration:

    - If USE_FAKE_EMBEDDINGS=true, returns FakeEmbeddings.
    - Otherwise, returns OpenAIEmbeddings using the configured model and key.
    """
    if settings.USE_FAKE_EMBEDDINGS:
        return FakeEmbeddings(dim=64)
    else:
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )


def get_embedding_client() -> Any:
    """Public getter for the embedding client (real or fake)."""
    return _get_embedding_client()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Helper used by ingestion to embed a batch of texts.

    Under the hood, this uses either OpenAIEmbeddings or FakeEmbeddings,
    depending on USE_FAKE_EMBEDDINGS.
    """
    client = _get_embedding_client()
    return client.embed_documents(texts)
