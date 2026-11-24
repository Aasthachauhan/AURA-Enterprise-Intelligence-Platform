"""Generate binary test files: sample_prd.docx and sample_financials.xlsx."""
import os
import openpyxl
from docx import Document

os.makedirs("datasets", exist_ok=True)

# 1. Create sample_prd.docx
doc = Document()
doc.add_heading("Product Requirements Document: AURA Platform", 0)

doc.add_heading("1. Executive Summary", level=1)
doc.add_paragraph(
    "AURA is an enterprise intelligence platform integrating multi-agent orchestration, "
    "grounded RAG, and MCP tool execution."
)

doc.add_heading("2. Requirements Matrix", level=1)
table = doc.add_table(rows=1, cols=3)
hdr_cells = table.rows[0].cells
hdr_cells[0].text = "ID"
hdr_cells[1].text = "Requirement Description"
hdr_cells[2].text = "Priority"

rows_data = [
    ("REQ-001", "Support multi-format file parsing (PDF, DOCX, XLSX, CSV, MD, HTML)", "P0"),
    ("REQ-002", "Enforce SHA-256 duplicate detection and version tracking", "P0"),
    ("REQ-003", "Hybrid retrieval combining dense vector similarity with BM25 keywords", "P0"),
    ("REQ-004", "Attach verifiable citations for all document-grounded claims", "P0"),
    ("REQ-005", "Fallback to insufficient evidence when facts are not supported in documents", "P0"),
]

for rid, desc, pri in rows_data:
    row_cells = table.add_row().cells
    row_cells[0].text = rid
    row_cells[1].text = desc
    row_cells[2].text = pri

doc.save("datasets/sample_prd.docx")
print("Saved datasets/sample_prd.docx")

# 2. Create sample_financials.xlsx
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Q1_Q2_Budget_Analysis"

headers = ["Department", "Quarter", "AllocatedBudgetUSD", "ActualSpendUSD", "VarianceUSD", "Status"]
ws.append(headers)

financial_rows = [
    ["AI Research", "Q1", 150000, 142000, 8000, "Under Budget"],
    ["AI Research", "Q2", 180000, 185000, -5000, "Over Budget"],
    ["Infrastructure", "Q1", 90000, 88000, 2000, "Under Budget"],
    ["Infrastructure", "Q2", 110000, 105000, 5000, "Under Budget"],
    ["QA Automation", "Q1", 60000, 59000, 1000, "Under Budget"],
    ["QA Automation", "Q2", 75000, 72000, 3000, "Under Budget"],
]

for row in financial_rows:
    ws.append(row)

wb.save("datasets/sample_financials.xlsx")
print("Saved datasets/sample_financials.xlsx")
