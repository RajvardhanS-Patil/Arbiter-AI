"""
Arbiter AI — Reports Routes
Handles retrieving compiled reports and exporting them in Markdown/JSON formats.
"""

from fastapi import APIRouter, HTTPException, Query
from models.schemas import ReportResponse, ExportResponse
import database as db_module
import json

router = APIRouter()

@router.get("/reports/{session_id}", response_model=ReportResponse)
async def get_report(session_id: str):
    """Retrieve the compiled report of a research session."""
    db = await db_module.get_db()
    try:
        report = await db_module.get_report_by_session(db, session_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found or not ready yet")
        return ReportResponse(**report)
    finally:
        await db.close()


@router.get("/reports/{session_id}/export", response_model=ExportResponse)
async def export_report(session_id: str, format: str = Query("markdown", regex="^(markdown|json)$")):
    """Export the report in Markdown or JSON format."""
    db = await db_module.get_db()
    try:
        report = await db_module.get_report_by_session(db, session_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found or not ready yet")
        
        session = await db_module.get_session(db, session_id)
        query = session["query"] if session else "Research"
        
        claims_rows = await db_module.get_claims_by_session(db, session_id)
        
        filename = f"arbiter_report_{session_id[:8]}"
        
        if format == "json":
            # Package everything nicely
            full_data = {
                "report": report,
                "claims": claims_rows,
                "query": query
            }
            content = json.dumps(full_data, indent=2, default=str)
            filename += ".json"
        else:
            # Generate clean Markdown
            md = []
            md.append(f"# Arbiter AI Fact-Verification Report: {report['title']}")
            md.append(f"\n**Investigation Topic:** {query}")
            md.append(f"**Overall Confidence Score:** {report['overall_confidence']}%")
            md.append(f"**Total Sources Evaluated:** {report['total_sources']}")
            md.append(f"**Contradictions Identified:** {report['contradiction_count']}")
            md.append(f"**Processing Duration:** {report['processing_time']} seconds")
            md.append("\n## Executive Summary")
            md.append(report["executive_summary"])
            
            # Sections
            sections = report.get("sections", [])
            for sec in sections:
                md.append(f"\n### Section: {sec['title']} (Confidence: {sec['section_confidence']}%)")
                md.append(sec["content"])
                
            # Claims listing
            md.append("\n## Interrogated Claims")
            for i, claim in enumerate(claims_rows, 1):
                status_emoji = "[VERIFIED]" if claim["verification_status"] == "verified" else "[DISPUTED]" if claim["verification_status"] == "disputed" else "[UNCERTAIN]"
                md.append(f"\n{i}. {status_emoji} **Claim:** \"{claim['text']}\"")
                md.append(f"   - **Verdict:** {claim['verdict'].upper()} (Confidence: {claim['confidence_score']}%)")
                md.append(f"   - **Category:** {claim['category']}")
                md.append(f"   - **Judge Reasoning:** {claim['judge_reasoning']}")
                
                # Get sources for this claim
                sources = await db_module.get_sources_by_claim(db, claim["id"])
                if sources:
                    md.append("   - **Cited Sources:**")
                    for s in sources:
                        md.append(f"     - [{s['title']}]({s['url']}) (Domain: {s['domain']}, Credibility: {s['credibility_score']}% - {s['credibility_tier']})")
            
            content = "\n".join(md)
            filename += ".md"
            
        return ExportResponse(
            format=format,
            content=content,
            filename=filename
        )
    finally:
        await db.close()
