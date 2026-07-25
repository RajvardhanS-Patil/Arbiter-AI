"""
Arbiter AI — Verifier Agent
Cross-verifies claims against independent sources.
Searches for corroborating and contradicting evidence.
"""

import uuid
from agents.base_agent import BaseAgent
from services.llm_service import llm_service
from services.search_service import search_service
from services.credibility_service import credibility_service
from services.claim_dna_service import claim_dna_service
from config import settings
import database as db_module


class VerifierAgent(BaseAgent):
    """
    🛡️ The Verifier
    Takes each claim and cross-references against independent sources.
    """
    
    AGENT_NAME = "verifier"
    AGENT_EMOJI = "🛡️"
    
    async def process(self, session_id: str, data: list[dict]) -> list[dict]:
        """
        Cross-verify each claim against independent sources.
        
        Args:
            data: List of claims from the Investigator
            
        Returns:
            Enriched claims with verification metadata
        """
        claims = data
        await self.start(session_id)
        
        database = await db_module.get_db()
        
        try:
            verified_claims = []
            
            for i, claim in enumerate(claims):
                await self.emit_progress(
                    i + 1, len(claims),
                    f"🛡️ Verifying: {claim['text'][:60]}..."
                )
                
                claim_id = claim.get("id", str(uuid.uuid4()))
                
                # Step 1: Search for corroborating evidence
                corroborating = await search_service.search_web(
                    f"evidence supporting: {claim['text'][:100]}",
                    max_results=settings.MAX_SOURCES_PER_CLAIM
                )
                
                # Step 2: Search for contradicting evidence
                contradicting = await search_service.search_web(
                    f"evidence against OR debunked: {claim['text'][:100]}",
                    max_results=3
                )
                
                # Step 3: Score credibility of new sources
                for source_list, relationship in [(corroborating, "corroborating"), 
                                                   (contradicting, "contradicting")]:
                    for source in source_list:
                        cred = credibility_service.score_source(
                            source.get("url", ""),
                            source.get("title", ""),
                            source.get("snippet", "")
                        )
                        source["credibility_score"] = cred["credibility_score"]
                        source["credibility_tier"] = cred["credibility_tier"]
                        
                        # Save to database
                        source_record = {
                            "id": str(uuid.uuid4()),
                            "claim_id": claim_id,
                            "session_id": session_id,
                            "url": source.get("url", ""),
                            "title": source.get("title", ""),
                            "domain": source.get("domain", ""),
                            "credibility_score": cred["credibility_score"],
                            "credibility_tier": cred["credibility_tier"],
                            "snippet": source.get("snippet", ""),
                            "relationship": relationship
                        }
                        await db_module.create_source(database, source_record)
                
                # Step 4: Use LLM to analyze verification
                verification = await self._analyze_verification(
                    claim["text"], corroborating, contradicting
                )
                
                # Step 5: Determine verification status
                status = verification.get("status", "unverified")
                confidence_boost = verification.get("confidence_change", 0)
                
                new_confidence = min(100, max(0, 
                    claim.get("confidence_score", 30) + confidence_boost
                ))
                
                # Update claim
                claim["verification_status"] = status
                claim["confidence_score"] = new_confidence
                claim["corroborating_sources"] = corroborating
                claim["contradicting_sources"] = contradicting
                claim["verification_analysis"] = verification.get("analysis", "")
                
                # Update in database
                await db_module.update_claim(database, claim_id, {
                    "verification_status": status,
                    "confidence_score": new_confidence,
                    "last_verified": "datetime('now')"
                })
                
                # Update DNA fingerprint
                if claim.get("dna_fingerprint"):
                    event = claim_dna_service.create_event(
                        claim_id, session_id, "VERIFIED", self.AGENT_NAME,
                        {
                            "corroborating_count": len(corroborating),
                            "contradicting_count": len(contradicting),
                            "status": status,
                            "confidence_change": f"+{confidence_boost}" if confidence_boost > 0 else str(confidence_boost)
                        }
                    )
                    await db_module.create_claim_event(database, event)
                    
                    claim["dna_fingerprint"] = claim_dna_service.update_fingerprint(
                        claim["dna_fingerprint"], event
                    )
                
                # Emit verification event
                await self.emit_event(
                    "claim_verified",
                    f"{'✅' if status == 'verified' else '⚠️' if status == 'disputed' else '❓'} "
                    f"Claim {status}: {claim['text'][:60]}...",
                    to_agent="devils_advocate",
                    metadata={
                        "claim_id": claim_id,
                        "status": status,
                        "confidence": new_confidence,
                        "corroborating": len(corroborating),
                        "contradicting": len(contradicting)
                    }
                )
                
                verified_claims.append(claim)
            
            # Update session
            verified_count = sum(1 for c in verified_claims if c.get("verification_status") == "verified")
            disputed_count = sum(1 for c in verified_claims if c.get("verification_status") == "disputed")
            
            await db_module.update_session(database, session_id, {
                "verified_claims": verified_count,
                "disputed_claims": disputed_count,
                "current_agent": "devils_advocate"
            })
            
            await self.complete(
                session_id,
                f"🛡️ Verifier completed: {verified_count} verified, {disputed_count} disputed out of {len(claims)}"
            )
            
            return verified_claims
            
        except Exception as e:
            await self.error(session_id, str(e))
            raise
        finally:
            await database.close()
    
    async def _analyze_verification(self, claim_text: str, 
                                     corroborating: list[dict],
                                     contradicting: list[dict]) -> dict:
        """Use LLM to analyze verification evidence."""
        
        corr_text = "\n".join([
            f"- [{s.get('title', 'Source')}] ({s.get('credibility_tier', 'UNKNOWN')}): {s.get('snippet', '')[:200]}"
            for s in corroborating[:5]
        ]) or "No corroborating sources found."
        
        contra_text = "\n".join([
            f"- [{s.get('title', 'Source')}] ({s.get('credibility_tier', 'UNKNOWN')}): {s.get('snippet', '')[:200]}"
            for s in contradicting[:3]
        ]) or "No contradicting sources found."
        
        prompt = f"""Analyze the verification evidence for this claim:

CLAIM: "{claim_text}"

CORROBORATING EVIDENCE:
{corr_text}

CONTRADICTING EVIDENCE:
{contra_text}

Based on the evidence, determine:
1. Is the claim verified, disputed, or unverifiable?
2. How much should the confidence change? (range: -30 to +40)
3. Brief analysis of the evidence quality

Respond with ONLY valid JSON:
{{
    "status": "verified" or "disputed" or "unverified",
    "confidence_change": <number -30 to 40>,
    "analysis": "<brief analysis>"
}}"""
        
        result = await llm_service.generate_json(prompt, temperature=0.3)
        
        if isinstance(result, dict):
            # Clamp confidence change
            change = result.get("confidence_change", 0)
            if isinstance(change, (int, float)):
                result["confidence_change"] = max(-30, min(40, change))
            else:
                result["confidence_change"] = 0
            return result
        
        return {"status": "unverified", "confidence_change": 0, "analysis": "Unable to verify"}


# Singleton instance
verifier_agent = VerifierAgent()
