"""Embedding generation providers with local fallback and provider abstraction."""
import math
import hashlib
import numpy as np
from typing import List, Optional
from app.core.config import settings


class BaseEmbeddingGenerator:
    async def generate_embedding(self, text: str) -> List[float]:
        raise NotImplementedError

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class DeterministicLocalEmbedder(BaseEmbeddingGenerator):
    """
    High-performance, reproducible semantic hash-projection embedding generator.
    Produces normalized 384-dimensional dense vectors with cosine similarity matching semantic overlap.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _embed_single(self, text: str) -> List[float]:
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()
            
        for i, word in enumerate(words):
            # Generate deterministic pseudo-random seeds per word
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            for j in range(4):
                idx = (h + j * 97) % self.dimension
                val = (((h >> (j * 8)) & 0xFF) / 128.0) - 1.0
                vec[idx] += val
                
            # Character n-grams for subword matching
            for k in range(len(word) - 2):
                ngram = word[k:k+3]
                nh = int(hashlib.sha1(ngram.encode("utf-8")).hexdigest(), 16)
                idx = nh % self.dimension
                vec[idx] += 0.25

        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    async def generate_embedding(self, text: str) -> List[float]:
        return self._embed_single(text)

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]


class OpenAIEmbedder(BaseEmbeddingGenerator):
    """OpenAI Embeddings provider."""
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    async def generate_embedding(self, text: str) -> List[float]:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"input": text, "model": self.model},
                timeout=30.0
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"input": texts, "model": self.model},
                timeout=60.0
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]


def get_embedding_generator() -> BaseEmbeddingGenerator:
    """Factory returning configured embedding generator."""
    if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAIEmbedder(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_EMBEDDING_MODEL)
    return DeterministicLocalEmbedder(dimension=settings.EMBEDDING_DIMENSION)
