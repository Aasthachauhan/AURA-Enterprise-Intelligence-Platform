"""Script to generate brand new, distinct enterprise test documents.
Covers PDF, DOCX, XLSX, CSV, MD, and TXT formats for comprehensive user testing.
"""
import os
from pathlib import Path

DATASET_DIR = Path("datasets/new_test_files")
DATASET_DIR.mkdir(parents=True, exist_ok=True)

# 1. Generate PDF: Healthcare HIPAA Compliance & BAA Agreement
def generate_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    pdf_path = DATASET_DIR / "healthcare_hipaa_compliance.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1e3a8a"))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=13, leading=16, textColor=colors.HexColor("#1e40af"))
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph("Healthcare Business Associate Agreement & HIPAA Security Specification", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Document Reference: BAA-SEC-2026-V4 | Classification: Confidential / HIPAA ePHI", h2_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "This Business Associate Agreement ('Agreement') is entered into by and between Apex Health Systems ('Covered Entity') "
        "and CloudScale AI Solutions ('Business Associate') to govern the safeguarding, transmission, and processing of "
        "Protected Health Information (PHI) and electronic Protected Health Information (ePHI) pursuant to the Health Insurance "
        "Portability and Accountability Act of 1996 (HIPAA) and the HITECH Act regulations.", body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Section 1: Permitted Uses and Disclosures", h2_style))
    story.append(Paragraph(
        "Business Associate agrees to not use or disclose Protected Health Information other than as permitted or required "
        "by the Agreement or as Required by Law. Business Associate shall utilize appropriate physical, administrative, and "
        "technical safeguards in compliance with 45 CFR § 164.312 to prevent any unauthorized disclosure of electronic PHI.", body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Section 2: Security Rule Safeguards & Technical Standards", h2_style))
    table_data = [
        ["Control Requirement", "HIPAA Reference", "Technical Implementation", "Audit Status"],
        ["Data Encryption at Rest", "§ 164.312(a)(2)(iv)", "FIPS 140-3 Validated AES-256 GCM", "Compliant"],
        ["Transmission Security", "§ 164.312(e)(1)", "TLS 1.3 with Strict HSTS Header", "Compliant"],
        ["Emergency Access Procedure", "§ 164.312(a)(2)(ii)", "Hardware MFA + Dual-Authorized Vault", "Compliant"],
        ["Audit Logs & Review", "§ 164.312(b)", "Immutable WORM Storage, 6-Year Retention", "Compliant"],
        ["Breach Notification SLA", "§ 164.410", "Notification to Covered Entity within 24 Hours", "Compliant"]
    ]
    t = Table(table_data, colWidths=[130, 100, 180, 70])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 3: Indemnification and Statutory Penalties", h2_style))
    story.append(Paragraph(
        "In the event of a breach of unsecured ePHI attributable to Business Associate's gross negligence or non-compliance, "
        "Business Associate shall defend and hold harmless Covered Entity against any Tier 4 civil monetary penalties "
        "assessed by the Department of Health and Human Services (HHS) Office for Civil Rights (OCR), up to a liability cap of $10,000,000.", body_style
    ))
    doc.build(story)
    print(f"Generated: {pdf_path}")

# 2. Generate Word DOCX: Cloud Migration Architecture Specification
def generate_docx():
    import docx
    from docx.shared import Inches, Pt, RGBColor

    doc_path = DATASET_DIR / "cloud_migration_spec.docx"
    doc = docx.Document()

    title = doc.add_heading("Enterprise Cloud Modernization & Multi-Region Migration Spec", level=0)
    p = doc.add_paragraph("Target Infrastructure: AWS Multi-Region (us-east-1 / us-west-2) | Target SLA: 99.99% Availability")
    p.runs[0].font.italic = True

    doc.add_heading("1. Executive Architecture Summary", level=1)
    doc.add_paragraph(
        "This engineering blueprint defines the migration of our legacy on-premises monolithic core banking platform "
        "to a cloud-native, containerized architecture deployed on Amazon Elastic Kubernetes Service (EKS) across dual active-active regions."
    )

    doc.add_heading("2. Target Component Specifications", level=1)
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Subsystem"
    hdr_cells[1].text = "Cloud Architecture"
    hdr_cells[2].text = "SLA Target"
    hdr_cells[3].text = "Redundancy"

    specs = [
        ("API Gateway", "Kong Enterprise Ingress with Envoy", "< 15ms latency", "Multi-AZ active/active"),
        ("Compute Cluster", "EKS Managed Nodes (c6i.4xlarge)", "99.99% Uptime", "3 AZs per region with Karpenter autoscaling"),
        ("Vector & Dense Database", "Amazon Aurora PostgreSQL + pgvector", "< 50ms query time", "Dual-Region Global Database with < 1s lag"),
        ("Caching Tier", "Amazon ElastiCache Redis 7.2 Multi-AZ", "< 2ms hit latency", "Auto-failover replica shards"),
        ("Event Streaming", "Apache Kafka on AWS MSK", "Zero Data Loss (RPO=0)", "3 Brokers replicated across separate AZs")
    ]
    for sub, arch, sla, red in specs:
        row_cells = table.add_row().cells
        row_cells[0].text = sub
        row_cells[1].text = arch
        row_cells[2].text = sla
        row_cells[3].text = red

    doc.add_heading("3. Failover Protocol and Recovery Metrics", level=1)
    doc.add_paragraph(
        "In the event of a full primary region failure in us-east-1, Route 53 DNS failover triggers health check diversion "
        "to us-west-2 within 30 seconds. The target Recovery Point Objective (RPO) is strictly 0 seconds for transactions, "
        "and the Recovery Time Objective (RTO) is less than 90 seconds."
    )
    doc.save(str(doc_path))
    print(f"Generated: {doc_path}")

# 3. Generate Excel XLSX: Vendor Security Assessment Matrix
def generate_xlsx():
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb_path = DATASET_DIR / "vendor_security_matrix.xlsx"
    wb = openpyxl.Workbook()

    # Sheet 1: Vendor Assessments
    ws1 = wb.active
    ws1.title = "Vendor_Assessments"

    headers1 = ["Vendor Name", "Domain", "SOC2 Type II", "ISO 27001", "FedRAMP", "Risk Rating", "Annual Spend USD", "Audit Status"]
    ws1.append(headers1)

    vendors = [
        ["Snowflake Inc.", "Data Warehouse", "Certified (2025)", "Certified", "Moderate", "Low", 420000, "Approved"],
        ["Databricks Core", "Lakehouse Analytics", "Certified (2025)", "Certified", "High", "Low", 380000, "Approved"],
        ["Twilio Communications", "Customer Messaging", "Certified (2024)", "Certified", "In-Process", "Medium", 125000, "Approved with Exceptions"],
        ["Workday HCM", "HR & Payroll", "Certified (2025)", "Certified", "High", "Low", 650000, "Approved"],
        ["Legacy CRM LegacySoft", "Sales Tracking", "Expired (2023)", "None", "None", "High", 95000, "Remediation Pending"],
        ["Anthropic PBC", "AI Model Provider", "Certified (2025)", "Certified", "In-Process", "Low", 240000, "Approved"]
    ]
    for v in vendors:
        ws1.append(v)

    # Sheet 2: Compliance Gaps
    ws2 = wb.create_sheet(title="Compliance_Gaps")
    headers2 = ["Finding ID", "Vendor", "Severity", "Deficiency Description", "Remediation SLA", "Owner"]
    ws2.append(headers2)

    gaps = [
        ["GAP-2026-01", "LegacySoft", "Critical", "Missing TLS 1.3 enforcement and lack of annual penetration test report", "30 Days", "Security Ops"],
        ["GAP-2026-02", "Twilio", "Medium", "Subprocessor notifications delayed beyond 30-day contractual window", "60 Days", "Vendor Management"],
        ["GAP-2026-03", "Anthropic", "Low", "Model weights retention policy clarification needed for internal review", "90 Days", "Legal AI Counsel"]
    ]
    for g in gaps:
        ws2.append(g)

    # Style header row
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    for ws in [ws1, ws2]:
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(str(wb_path))
    print(f"Generated: {wb_path}")

# 4. Generate Markdown: Production Incident Post-Mortem
def generate_md():
    md_path = DATASET_DIR / "incident_postmortem.md"
    content = """# Post-Mortem: SEV-1 Database Replication Lag & Aurora Cluster Failover
**Date of Incident:** 2026-11-18  
**Incident Commander:** Principal SRE Lead  
**Impacted Services:** Core Transaction API, Vector Embedding Pipeline, Knowledge Graph Sync  
**Total Downtime / Degraded Operations:** 24 minutes  

---

## 1. Executive Summary
On November 18, 2026, at 14:12 UTC, a transient network partition between AWS us-east-1a and us-east-1b caused an abrupt spike in Aurora PostgreSQL replication lag, exceeding the 2500ms safety threshold. The automated failover mechanism promoted the replica in us-east-1c to primary. During the 90-second promotion window, API writes encountered HTTP 503 errors. Full automated recovery occurred at 14:36 UTC without transaction loss.

## 2. Root Cause Analysis (5 Whys)
1. **Why did API write calls fail?** The primary database instance transitioned to read-only during failover promotion.
2. **Why did failover trigger?** The replication lag watchdog detected a 3200ms lag exceeding the 2500ms health check threshold.
3. **Why did replication lag spike?** High-volume batch re-indexing of 50,000 PDF documents saturated the I/O bus during an unexpected network packet drop.
4. **Why was batch ingestion uncapped?** The background document ingestion worker did not have exponential backoff or write rate-limiting enabled.
5. **Why was rate-limiting absent?** Ingestion pipeline v1 assumed dedicated Aurora read-replicas for batch embedding generation.

## 3. Preventive Action Items & SLAs
- **ACT-01 (P0):** Implement token-bucket rate limiter (50 docs/min) on ingestion queue workers. *Owner: Platform Eng | Status: In Progress*
- **ACT-02 (P0):** Route all vector embedding read queries exclusively to dedicated read-replicas. *Owner: Data Eng | Status: Completed*
- **ACT-03 (P1):** Increase replication lag tolerance window from 2.5s to 5.0s during peak hours. *Owner: SRE | Status: Completed*
- **ACT-04 (P2):** Configure automated Slack pager alerting when replication lag exceeds 1000ms. *Owner: DevOps | Status: Completed*
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {md_path}")

# 5. Generate CSV: Q3 Security Audit & CVE Vulnerability Matrix
def generate_csv():
    csv_path = DATASET_DIR / "q3_security_audit.csv"
    content = """Vulnerability_ID,Component,CVE_Identifier,CVSS_Score,Severity,Exploitability,Patch_SLA_Days,Remediation_Status
SEC-CVE-001,FastAPI_Web_Framework,CVE-2025-43210,5.3,Medium,Proof-of-Concept,30,Patched_v0.115
SEC-CVE-002,OpenSSL_TLS_Layer,CVE-2025-11928,7.5,High,Theoretical,14,Patched_v3.2.1
SEC-CVE-003,PostgreSQL_Driver,CVE-2024-99812,4.1,Low,None,60,Accepted_Risk
SEC-CVE-004,PyJWT_Token_Parser,CVE-2025-22345,8.8,High,Active_In_Wild,7,Remediated_Strict_Verify
SEC-CVE-005,Docker_Base_Image,CVE-2025-33100,6.2,Medium,None,30,Scheduled_Q4
SEC-CVE-006,Redis_Cluster_Client,CVE-2024-77211,3.2,Low,None,90,Verified_Safe"""
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Generated: {csv_path}")

# 6. Generate TXT: Master Enterprise Software Licensing Agreement
def generate_txt():
    txt_path = DATASET_DIR / "legal_licensing_agreement.txt"
    content = """MASTER ENTERPRISE SOFTWARE LICENSE & SUPPORT AGREEMENT (MLA)

Dated: January 15, 2026
Between:
1. QUANTUM ENTERPRISES INC., a Delaware Corporation with its principal office at 500 Technology Way, San Francisco, CA ("Licensor")
2. GLOBAL ENTERPRISE PARTNERS LLC ("Licensee")

1. GRANT OF LICENSE
Subject to the terms and conditions of this Agreement, Licensor hereby grants to Licensee a non-exclusive, non-transferable, worldwide commercial license to deploy and operate the AURA Enterprise Intelligence Platform across up to 10,000 internal enterprise users.

2. SERVICE LEVEL AGREEMENT (SLA) & SUPPORT TIERS
2.1 Uptime Guarantee: Licensor warrants that the Core SaaS Intelligence Platform shall achieve 99.95% Availability during each calendar month.
2.2 SLA Penalty Credits:
- If Availability is between 99.0% and 99.95%, Licensee is entitled to a 10% credit of monthly billing fees.
- If Availability falls below 99.0%, Licensee is entitled to a 25% credit of monthly billing fees.
2.3 Support Response Times:
- Priority 1 (System Down / SEV-1): 15-minute initial response, 24x7x365 coverage.
- Priority 2 (Severe Degradation): 1-hour initial response.
- Priority 3 (Standard Inquiries): 4-hour business hours response.

3. INDEMNIFICATION & LIABILITY
Licensor agrees to defend, indemnify, and hold harmless Licensee against any third-party intellectual property infringement claims arising from the authorized use of the licensed software.
The aggregate liability of either party under this Agreement shall not exceed the total fees paid by Licensee in the twelve (12) months preceding the incident, except for gross negligence, willful misconduct, or breach of Section 4 (Confidentiality).

4. GOVERNING LAW AND JURISDICTION
This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of law principles. Any dispute arising hereunder shall be resolved in the state or federal courts situated in New Castle County, Delaware.
"""
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Generated: {txt_path}")

if __name__ == "__main__":
    generate_pdf()
    generate_docx()
    generate_xlsx()
    generate_md()
    generate_csv()
    generate_txt()
    print("All fresh test files successfully created in datasets/new_test_files/!")
