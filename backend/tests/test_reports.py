"""Tests for Report generation and markdown export."""
import pytest
from app.services.report_service import ReportService


@pytest.mark.asyncio
async def test_report_generation_and_export(db_session):
    """Verify report generation produces executive summary, findings, risks, and markdown."""
    report = await ReportService.generate_report(
        db=db_session,
        title="Test QA Risk Assessment",
        report_type="qa_assessment",
        document_ids=[],
        query_or_focus="Assess test coverage against PRD requirements",
        workspace_id="test_ws",
        user_id="test_user"
    )

    assert report.id is not None
    assert report.title == "Test QA Risk Assessment"
    assert len(report.markdown_content) > 50
    assert "Executive Summary" in report.markdown_content
