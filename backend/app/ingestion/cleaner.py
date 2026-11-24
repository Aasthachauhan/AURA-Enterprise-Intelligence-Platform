"""Text sanitization, normalization, and indirect prompt injection defense."""
import re
import unicodedata


class TextCleaner:
    # Common prompt injection patterns found in untrusted uploaded docs
    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+a\s+different\s+ai", re.IGNORECASE),
        re.compile(r"system\s+prompt\s*:\s*", re.IGNORECASE),
        re.compile(r"<\|im_start\|>", re.IGNORECASE),
        re.compile(r"<\|im_end\|>", re.IGNORECASE),
        re.compile(r"\[INST\]", re.IGNORECASE),
        re.compile(r"\[/INST\]", re.IGNORECASE),
    ]

    @classmethod
    def clean(cls, text: str) -> str:
        """Normalize unicode, whitespace, and sanitize control characters."""
        if not text:
            return ""
            
        # Normalize unicode
        text = unicodedata.normalize("NFKC", text)
        
        # Replace non-printable characters except whitespace
        text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or unicodedata.category(ch)[0] != "C")
        
        # Collapse excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        # Defuse potential indirect prompt injection vectors
        for pattern in cls.INJECTION_PATTERNS:
            text = pattern.sub("[FILTERED_POTENTIAL_INJECTION_PROMPT]", text)
            
        return text.strip()
