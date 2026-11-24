"""Okapi BM25 keyword search index."""
import math
import re
from typing import List, Dict, Any, Optional, Tuple


class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avgdl = 0.0
        # doc_id -> list of tokens
        self.doc_tokens: Dict[str, List[str]] = {}
        # doc_id -> length
        self.doc_lens: Dict[str, int] = {}
        # doc_id -> metadata
        self.doc_metadata: Dict[str, Dict[str, Any]] = {}
        # term -> doc_id -> term_frequency
        self.inverted_index: Dict[str, Dict[str, int]] = {}
        # term -> idf
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        """Simple alphanumeric tokenizer with lowercasing."""
        return re.findall(r"\w+", text.lower())

    def add_document(self, doc_id: str, chunk_id: str, text: str, metadata: Dict[str, Any]) -> None:
        """Add or update a document chunk in the BM25 index."""
        unique_id = f"{doc_id}:{chunk_id}"
        tokens = self._tokenize(text)
        self.doc_tokens[unique_id] = tokens
        self.doc_lens[unique_id] = len(tokens)
        self.doc_metadata[unique_id] = {**metadata, "chunk_id": chunk_id, "text": text}
        
        # Update inverted index
        for token in tokens:
            if token not in self.inverted_index:
                self.inverted_index[token] = {}
            self.inverted_index[token][unique_id] = self.inverted_index[token].get(unique_id, 0) + 1
            
        self.corpus_size = len(self.doc_tokens)
        total_len = sum(self.doc_lens.values())
        self.avgdl = total_len / self.corpus_size if self.corpus_size > 0 else 0.0
        self._recompute_idf()

    def _recompute_idf(self) -> None:
        """Calculate IDF for all vocabulary terms."""
        for term, posting in self.inverted_index.items():
            doc_freq = len(posting)
            # Standard Lucene/BM25 IDF formula
            self.idf[term] = math.log(1.0 + (self.corpus_size - doc_freq + 0.5) / (doc_freq + 0.5))

    def search(
        self,
        query: str,
        top_k: int = 10,
        workspace_id: Optional[str] = None,
        filter_document_ids: Optional[List[str]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search BM25 index and return (unique_id, score, metadata)."""
        query_tokens = self._tokenize(query)
        scores: Dict[str, float] = {}

        for token in query_tokens:
            if token not in self.inverted_index:
                continue
            idf_val = self.idf.get(token, 0.0)
            postings = self.inverted_index[token]

            for doc_uid, tf in postings.items():
                meta = self.doc_metadata.get(doc_uid, {})
                if workspace_id and meta.get("workspace_id") != workspace_id:
                    continue
                if filter_document_ids and meta.get("document_id") not in filter_document_ids:
                    continue

                doc_len = self.doc_lens[doc_uid]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avgdl or 1.0)))
                scores[doc_uid] = scores.get(doc_uid, 0.0) + idf_val * (numerator / denominator)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(doc_uid, score, self.doc_metadata[doc_uid]) for doc_uid, score in ranked]


# Global in-memory BM25 index instance
bm25_index = BM25Index()
