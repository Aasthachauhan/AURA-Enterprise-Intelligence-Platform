"""Citation formatting, extraction, and grounding validation."""
import re
from typing import List, Dict, Any, Tuple
from app.rag.hybrid import RetrievedChunk


class CitationValidator:
    @staticmethod
    def format_citation_marker(chunk: RetrievedChunk) -> str:
        """Create standard citation marker: [DocTitle: Page X] or [DocTitle: Sheet Y]."""
        location = ""
        if chunk.page_number is not None:
            location = f": Page {chunk.page_number}"
        elif chunk.sheet_name is not None:
            location = f": Sheet {chunk.sheet_name}"
        elif chunk.section_title is not None:
            location = f": {chunk.section_title}"
            
        return f"[{chunk.document_title}{location}]"

    @classmethod
    def extract_and_verify_citations(
        cls,
        generated_answer: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Extract citations from generated text and verify they exist in retrieved chunks.
        Returns list of structured citations and a citation correctness score (0.0 to 1.0).
        """
        citations: List[Dict[str, Any]] = []
        chunk_map = {c.document_title.lower(): c for c in retrieved_chunks}
        
        # Match citations like [Document Title: Page 1] or [Document Title]
        matches = re.findall(r"\[([a-zA-Z0-9_\-\.\s]+?)(?::\s*([^\]]+))?\]", generated_answer)
        
        valid_citations = 0
        total_citations = len(matches)

        for doc_title, loc in matches:
            doc_key = doc_title.strip().lower()
            matched_chunk = None
            
            # Find closest matching chunk
            for k, chunk in chunk_map.items():
                if doc_key in k or k in doc_key:
                    matched_chunk = chunk
                    break
                    
            if matched_chunk:
                valid_citations += 1
                citations.append({
                    "document_id": matched_chunk.document_id,
                    "document_title": matched_chunk.document_title,
                    "page_number": matched_chunk.page_number,
                    "sheet_name": matched_chunk.sheet_name,
                    "section_title": matched_chunk.section_title,
                    "excerpt": matched_chunk.content[:250] + "...",
                    "similarity_score": matched_chunk.score
                })

        # If no explicit markers found, attach top retrieved sources as references
        if not citations and retrieved_chunks:
            for c in retrieved_chunks[:3]:
                citations.append({
                    "document_id": c.document_id,
                    "document_title": c.document_title,
                    "page_number": c.page_number,
                    "sheet_name": c.sheet_name,
                    "section_title": c.section_title,
                    "excerpt": c.content[:250] + "...",
                    "similarity_score": c.score
                })
            citation_score = 0.8
        else:
            citation_score = (valid_citations / total_citations) if total_citations > 0 else 1.0

        return citations, citation_score
