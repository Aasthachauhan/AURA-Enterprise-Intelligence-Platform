"""Multi-format document parsers with structural and metadata extraction."""
import csv
import io
import os
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import pypdf
import docx
import openpyxl


class ParsedSection:
    def __init__(
        self,
        content: str,
        page_number: Optional[int] = None,
        sheet_name: Optional[str] = None,
        section_title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.page_number = page_number
        self.sheet_name = sheet_name
        self.section_title = section_title
        self.metadata = metadata or {}


class DocumentParser:
    @staticmethod
    def parse_pdf(file_path: str) -> List[ParsedSection]:
        """Extract text and metadata page by page from PDF."""
        sections = []
        reader = pypdf.PdfReader(file_path)
        total_pages = len(reader.pages)
        
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                sections.append(
                    ParsedSection(
                        content=text.strip(),
                        page_number=idx + 1,
                        section_title=f"Page {idx + 1}",
                        metadata={"total_pages": total_pages}
                    )
                )
        return sections

    @staticmethod
    def parse_docx(file_path: str) -> List[ParsedSection]:
        """Extract paragraphs, headings, and tables from DOCX."""
        sections = []
        doc = docx.Document(file_path)
        current_heading = "General Content"
        current_paragraphs = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if para.style and para.style.name.startswith("Heading"):
                if current_paragraphs:
                    sections.append(
                        ParsedSection(
                            content="\n".join(current_paragraphs),
                            section_title=current_heading
                        )
                    )
                    current_paragraphs = []
                current_heading = text
            else:
                current_paragraphs.append(text)
                
        if current_paragraphs:
            sections.append(
                ParsedSection(
                    content="\n".join(current_paragraphs),
                    section_title=current_heading
                )
            )
            
        # Parse tables
        for table_idx, table in enumerate(doc.tables):
            table_rows = []
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                table_rows.append(" | ".join(cells))
            if table_rows:
                sections.append(
                    ParsedSection(
                        content="Table " + str(table_idx + 1) + ":\n" + "\n".join(table_rows),
                        section_title=f"Table {table_idx + 1}"
                    )
                )
                
        return sections

    @staticmethod
    def parse_xlsx(file_path: str) -> List[ParsedSection]:
        """Extract spreadsheet sheets, headers, and rows from XLSX."""
        sections = []
        wb = openpyxl.load_workbook(file_path, data_only=True)
        
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            rows_data = []
            for row in sheet.iter_rows(values_only=True):
                # Filter out completely empty rows
                if any(v is not None for v in row):
                    formatted_cells = [str(v) if v is not None else "" for v in row]
                    rows_data.append(" | ".join(formatted_cells))
                    
            if rows_data:
                content = f"Sheet: {sheet_name}\n" + "\n".join(rows_data)
                sections.append(
                    ParsedSection(
                        content=content,
                        sheet_name=sheet_name,
                        section_title=f"Sheet: {sheet_name}",
                        metadata={"row_count": len(rows_data)}
                    )
                )
        return sections

    @staticmethod
    def parse_csv(file_path: str) -> List[ParsedSection]:
        """Extract CSV records with header preservation."""
        sections = []
        with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        if not rows:
            return sections
            
        headers = rows[0]
        rows_content = []
        for row in rows[1:]:
            pairs = [f"{h}: {val}" for h, val in zip(headers, row) if val.strip()]
            rows_content.append(", ".join(pairs))
            
        # Chunk into reasonable section batches
        batch_size = 50
        for i in range(0, len(rows_content), batch_size):
            batch = rows_content[i:i + batch_size]
            sections.append(
                ParsedSection(
                    content=f"CSV Records {i + 1} to {min(i + batch_size, len(rows_content))}:\n" + "\n".join(batch),
                    section_title=f"Records {i + 1}-{min(i + batch_size, len(rows_content))}",
                    metadata={"total_records": len(rows_content)}
                )
            )
        return sections

    @staticmethod
    def parse_html(file_path: str) -> List[ParsedSection]:
        """Extract text from HTML with structural tag preservation."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove scripts, styles
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
            
        title = soup.title.string if soup.title else "HTML Document"
        sections = []
        
        # Find headings or paragraphs
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text().strip()
            # Find next siblings until next heading
            content_nodes = []
            curr = h.next_sibling
            while curr and getattr(curr, "name", None) not in ["h1", "h2", "h3"]:
                if hasattr(curr, "get_text"):
                    c_text = curr.get_text().strip()
                    if c_text:
                        content_nodes.append(c_text)
                curr = curr.next_sibling
            
            body_text = "\n".join(content_nodes) if content_nodes else text
            sections.append(
                ParsedSection(
                    content=f"{text}\n{body_text}",
                    section_title=text
                )
            )
            
        if not sections:
            text = soup.get_text(separator="\n").strip()
            if text:
                sections.append(ParsedSection(content=text, section_title=title))
                
        return sections

    @staticmethod
    def parse_text_or_markdown(file_path: str) -> List[ParsedSection]:
        """Parse raw text or markdown with heading breakdown."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            
        sections = []
        current_title = "Document Body"
        current_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                if current_lines:
                    sections.append(
                        ParsedSection(
                            content="".join(current_lines).strip(),
                            section_title=current_title
                        )
                    )
                    current_lines = []
                current_title = stripped.lstrip("#").strip()
            else:
                current_lines.append(line)
                
        if current_lines:
            sections.append(
                ParsedSection(
                    content="".join(current_lines).strip(),
                    section_title=current_title
                )
            )
            
        return sections

    @classmethod
    def parse(cls, file_path: str, file_type: str) -> List[ParsedSection]:
        """Route to appropriate parser by file extension."""
        ft = file_type.lower().replace(".", "")
        if ft == "pdf":
            return cls.parse_pdf(file_path)
        elif ft in ["docx", "doc"]:
            return cls.parse_docx(file_path)
        elif ft in ["xlsx", "xls"]:
            return cls.parse_xlsx(file_path)
        elif ft == "csv":
            return cls.parse_csv(file_path)
        elif ft in ["html", "htm"]:
            return cls.parse_html(file_path)
        elif ft in ["md", "markdown", "txt"]:
            return cls.parse_text_or_markdown(file_path)
        else:
            # Fallback text parsing
            return cls.parse_text_or_markdown(file_path)
