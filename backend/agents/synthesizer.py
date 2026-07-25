"""
Arbiter AI — Synthesizer Agent
Compiles all judged claims into a coherent, citation-backed report
with executive summary, sections, and overall confidence scoring.
"""

import uuid
from datetime import datetime
from agents.base_agent import BaseAgent
from services.llm_service import llm_service
from services.claim_dna_service import claim_dna_service
import database as db_module


class SynthesizerAgent(BaseAgent):
    """
    📊 The Synthesizer
    Compiles all judged claims into a structured, citation-backed report.
    """
    
    AGENT_NAME = "synthesizer"
    AGENT_EMOJI = "📊"
    
    async def process(self, session_id: str, data: list[dict]) -> dict:
        """
        Compile all judged claims into a final report.
        
        Args:
            data: List of judged claims from the Judge
            
        Returns:
            Report dict with executive summary, sections, and metrics
        """
        claims = data
        await self.start(session_id)
        
        database = await db_module.get_db()
        
        try:
            # Step 1: Organize claims by category
            await self.emit_event(
                "agent_progress",
                "📊 Organizing claims into logical sections...",
                metadata={"step": "organize"}
            )
            
            categorized = self._categorize_claims(claims)
            
            # Step 2: Generate report title
            session = await db_module.get_session(database, session_id)
            query = session["query"] if session else "Research Report"
            
            title = await self._generate_title(query, claims)
            
            # Step 3: Generate sections with narrative
            await self.emit_event(
                "agent_progress",
                "✍️ Generating report sections with narrative...",
                metadata={"step": "generate_sections"}
            )
            
            sections = await self._generate_sections(query, categorized, claims)
            
            # Step 4: Generate executive summary
            await self.emit_event(
                "agent_progress",
                "📋 Composing executive summary...",
                metadata={"step": "executive_summary"}
            )
            
            # Calculate metrics
            accepted = [c for c in claims if c.get("verdict") == "accepted"]
            rejected = [c for c in claims if c.get("verdict") == "rejected"]
            uncertain = [c for c in claims if c.get("verdict") == "uncertain"]
            
            overall_confidence = (
                sum(c.get("confidence_score", 0) for c in claims) / len(claims)
                if claims else 0
            )
            
            # Count unique sources
            all_source_urls = set()
            for claim in claims:
                for s in claim.get("sources", []):
                    if s.get("url"):
                        all_source_urls.add(s["url"])
                for s in claim.get("corroborating_sources", []):
                    if s.get("url"):
                        all_source_urls.add(s["url"])
            
            total_sources = len(all_source_urls)
            
            # Count contradictions
            all_contradictions = []
            for claim in claims:
                all_contradictions.extend(claim.get("contradictions", []))
            # Deduplicate contradictions
            seen_pairs = set()
            unique_contradictions = []
            for c in all_contradictions:
                pair = tuple(sorted([c.get("claim_a_id", ""), c.get("claim_b_id", "")]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    unique_contradictions.append(c)
            
            executive_summary = await self._generate_executive_summary(
                query, claims, accepted, rejected, uncertain,
                overall_confidence, total_sources, len(unique_contradictions)
            )
            
            # Step 5: Calculate processing time
            if session and session.get("created_at"):
                try:
                    start_time = datetime.fromisoformat(session["created_at"].replace("Z", "+00:00"))
                    processing_time = (datetime.utcnow().replace(tzinfo=start_time.tzinfo) - start_time).total_seconds()
                except Exception:
                    processing_time = 0
            else:
                processing_time = 0
            
            # Step 6: Build and save report
            report = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "title": title,
                "executive_summary": executive_summary,
                "sections": sections,
                "overall_confidence": round(overall_confidence, 1),
                "total_sources": total_sources,
                "contradiction_count": len(unique_contradictions),
                "processing_time": round(processing_time, 1)
            }
            
            await db_module.create_report(database, report)
            
            # Update session as completed
            await db_module.update_session(database, session_id, {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "overall_confidence": round(overall_confidence, 1),
                "total_sources": total_sources,
                "contradiction_count": len(unique_contradictions),
                "processing_time": round(processing_time, 1),
                "current_agent": None
            })
            
            # Emit report ready event
            await self.emit_event(
                "report_ready",
                f"📊 Report compiled: '{title}' — {overall_confidence:.1f}% confidence",
                metadata={
                    "report_id": report["id"],
                    "title": title,
                    "overall_confidence": round(overall_confidence, 1),
                    "total_claims": len(claims),
                    "accepted": len(accepted),
                    "rejected": len(rejected),
                    "total_sources": total_sources
                }
            )
            
            await self.complete(
                session_id,
                f"📊 Synthesizer completed: Report '{title}' with {overall_confidence:.1f}% confidence"
            )
            
            return report
            
        except Exception as e:
            await self.error(session_id, str(e))
            raise
        finally:
            await database.close()
    
    def _categorize_claims(self, claims: list[dict]) -> dict[str, list[dict]]:
        """Group claims by category."""
        categories = {}
        for claim in claims:
            cat = claim.get("category", "general")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(claim)
        return categories
    
    async def _generate_title(self, query: str, claims: list[dict]) -> str:
        """Generate a report title using LLM."""
        prompt = f"""Generate a concise, professional report title for a fact-verification analysis about: "{query}"

The report covers {len(claims)} verified claims.

Respond with ONLY the title text, nothing else. Keep it under 10 words."""
        
        try:
            title = await llm_service.generate(prompt, temperature=0.5)
            return title.strip().strip('"').strip("'")
        except Exception:
            return f"Report: {query[:50]}"
    
    async def _generate_sections(self, query: str, categorized: dict, 
                                  all_claims: list[dict]) -> list[dict]:
        """Generate report sections with narrative text."""
        sections = []
        
        for category, claims in categorized.items():
            # Build claim summaries for this section
            claim_summaries = []
            for c in claims:
                verdict_icon = "✅" if c.get("verdict") == "accepted" else "❌" if c.get("verdict") == "rejected" else "⚠️"
                claim_summaries.append(
                    f"{verdict_icon} [{c.get('confidence_score', 0):.0f}%] {c['text']}"
                )
            
            claims_text = "\n".join(claim_summaries)
            
            prompt = f"""Write a brief analytical paragraph (3-5 sentences) synthesizing the following verified claims about "{query}" in the category "{category}":

{claims_text}

Requirements:
- Be objective and analytical
- Reference specific findings
- Note any contradictions or uncertainties
- Keep it concise and professional

Write ONLY the paragraph, no headers or formatting."""
            
            try:
                narrative = await llm_service.generate(prompt, temperature=0.4)
                narrative = narrative.strip()
            except Exception:
                narrative = f"Analysis of {len(claims)} claims in the {category} category."
            
            section_confidence = (
                sum(c.get("confidence_score", 0) for c in claims) / len(claims)
                if claims else 0
            )
            
            sections.append({
                "title": category.replace("_", " ").title(),
                "content": narrative,
                "claim_ids": [c.get("id", "") for c in claims],
                "section_confidence": round(section_confidence, 1)
            })
        
        return sections
    
    async def _generate_executive_summary(self, query: str, all_claims: list,
                                           accepted: list, rejected: list,
                                           uncertain: list, overall_confidence: float,
                                           total_sources: int, contradictions: int) -> str:
        """Generate the executive summary."""
        prompt = f"""Write a professional executive summary (4-6 sentences) for a fact-verification report about: "{query}"

Key metrics:
- Total claims analyzed: {len(all_claims)}
- Claims accepted: {len(accepted)}
- Claims rejected: {len(rejected)}
- Claims uncertain: {len(uncertain)}
- Overall confidence: {overall_confidence:.1f}%
- Total sources consulted: {total_sources}
- Contradictions found: {contradictions}

Top accepted claims:
{chr(10).join([f"- {c['text'][:100]}" for c in sorted(accepted, key=lambda x: x.get('confidence_score', 0), reverse=True)[:3]])}

Requirements:
- Professional, analytical tone
- Mention key findings and overall reliability
- Note significant contradictions if any
- Reference the multi-agent verification process

Write ONLY the summary paragraph."""
        
        try:
            summary = await llm_service.generate(prompt, temperature=0.4)
            return summary.strip()
        except Exception:
            return (
                f"This report analyzes {len(all_claims)} claims about {query}, "
                f"of which {len(accepted)} were accepted and {len(rejected)} were rejected "
                f"through multi-agent adversarial verification. "
                f"Overall confidence stands at {overall_confidence:.1f}% "
                f"based on {total_sources} consulted sources."
            )


# Singleton instance
synthesizer_agent = SynthesizerAgent()
