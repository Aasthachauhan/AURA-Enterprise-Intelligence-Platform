"""Configurable document chunker with overlap and metadata retention."""
from typing import List, Dict, Any, Optional
from app.ingestion.parsers import ParsedSection
from app.ingestion.cleaner import TextCleaner
from app.core.config import settings


class ChunkItem:
    def __init__(
        self,
        chunk_index: int,
        content: str,
        clean_content: str,
        page_number: Optional[int] = None,
        sheet_name: Optional[str] = None,
        section_title: Optional[str] = None,
        token_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_index = chunk_index
        self.content = content
        self.clean_content = clean_content
        self.page_number = page_number
        self.sheet_name = sheet_name
        self.section_title = section_title
        self.token_count = token_count
        self.metadata = metadata or {}


class DocumentChunker:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_sections(self, sections: List[ParsedSection]) -> List[ChunkItem]:
        """Split parsed sections into bounded overlapping chunks preserving metadata."""
        chunks: List[ChunkItem] = []
        global_index = 0

        for section in sections:
            clean_text = TextCleaner.clean(section.content)
            if not clean_text:
                continue

            # If section fits comfortably within chunk_size, keep as single chunk
            if len(clean_text) <= self.chunk_size:
                chunks.append(
                    ChunkItem(
                        chunk_index=global_index,
                        content=clean_text,
                        clean_content=clean_text,
                        page_number=section.page_number,
                        sheet_name=section.sheet_name,
                        section_title=section.section_title,
                        token_count=len(clean_text.split()),
                        metadata=section.metadata
                    )
                )
                global_index += 1
                continue

            # Recursive / character window chunking with overlap
            start = 0
            text_len = len(clean_text)

            while start < text_len:
                end = min(start + self.chunk_size, text_len)
                
                # If not at the end of text, attempt to break on paragraph or sentence boundary
                if end < text_len:
                    break_point = -1
                    for sep in ["\n\n", "\n", ". ", "; ", ", "]:
                        pos = clean_text.rfind(sep, start + self.chunk_overlap, end)
                        if pos != -1:
                            break_point = pos + len(sep)
                            break
                    if break_point != -1:
                        end = break_point

                chunk_text = clean_text[start:end].strip()
                if chunk_text:
                    chunks.append(
                        ChunkItem(
                            chunk_index=global_index,
                            content=chunk_text,
                            clean_content=chunk_text,
                            page_number=section.page_number,
                            sheet_name=section.sheet_name,
                            section_title=section.section_title,
                            token_count=len(chunk_text.split()),
                            metadata=section.metadata
                        )
                    )
                    global_index += 1

                if end >= text_len:
                    break
                # Advance with overlap
                start = max(end - self.chunk_overlap, start + 1)

        return chunks
