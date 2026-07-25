"""
Arbiter AI — Judge Agent
The arbitration agent that evaluates the debate between Verifier
and Devil's Advocate, applies multi-model consensus, and issues
final verdicts with confidence scores.
"""

import uuid
import math
from datetime import datetime
from agents.base_agent import BaseAgent
from services.llm_service import llm_service
from services.consensus_service import consensus_service
from services.claim_dna_service import claim_dna_service
from config import settings
import database as db_module


class JudgeAgent(BaseAgent):
    """
    ⚖️ The Judge
    Evaluates arguments from both sides, applies multi-model consensus,
    and issues final verdicts with confidence scores.
    """
    
    AGENT_NAME = "judge"
    AGENT_EMOJI = "⚖️"
    
    async def process(self, session_id: str, data: list[dict]) -> list[dict]:
        """
        Judge each claim by evaluating evidence from both sides.
        
        Args:
            data: List of challenged claims from Devil's Advocate
            
        Returns:
            Claims with final verdicts and confidence scores
        """
        claims = data
        await self.start(session_id)
        
        database = await db_module.get_db()
        
        try:
            judged_claims = []
            
            for i, claim in enumerate(claims):
                await self.emit_progress(
                    i + 1, len(claims),
                    f"⚖️ Judging: {claim['text'][:60]}..."
                )
                
                claim_id = claim.get("id", "")
                
                # Step 1: Run debate between Verifier and Devil's Advocate
                debate_data = await self._run_debate(claim, session_id)
                
                # Save debate to database
                await db_module.create_debate(database, {
                    "id": str(uuid.uuid4()),
                    "claim_id": claim_id,
                    "session_id": session_id,
                    "claim_text": claim["text"],
                    "rounds": debate_data.get("rounds", []),
                    "verdict": debate_data.get("verdict", {})
                })
                
                # Step 2: Multi-model consensus (if enabled)
                evidence_for = [
                    s.get("snippet", "") for s in claim.get("corroborating_sources", [])
                    if s.get("snippet")
                ][:3]
                
                evidence_against = claim.get("counter_arguments", [])[:3]
                
                consensus_result = await consensus_service.evaluate_claim(
                    claim["text"], evidence_for, evidence_against,
                    session_id, claim_id
                )
                
                # Save consensus votes to database
                for vote in consensus_result.get("votes", []):
                    await db_module.create_consensus_vote(database, vote)
                
                # Step 3: Calculate final confidence score
                final_score = self._calculate_final_confidence(
                    claim, debate_data, consensus_result
                )
                
                # Step 4: Issue verdict
                verdict = self._determine_verdict(final_score)
                judge_reasoning = debate_data.get("verdict", {}).get("reasoning", "")
                
                if consensus_result.get("details"):
                    judge_reasoning += f" | Consensus: {consensus_result['details']}"
                
                # Step 5: Apply temporal decay
                temporal_relevance = self._calculate_temporal_relevance(claim)
                
                # Update claim
                claim["confidence_score"] = final_score
                claim["verdict"] = verdict
                claim["judge_reasoning"] = judge_reasoning
                claim["temporal_relevance"] = temporal_relevance
                claim["consensus"] = consensus_result
                
                # Update in database
                await db_module.update_claim(database, claim_id, {
                    "confidence_score": final_score,
                    "verdict": verdict,
                    "judge_reasoning": judge_reasoning,
                    "temporal_relevance": temporal_relevance
                })
                
                # Create JUDGED genealogy event
                event = claim_dna_service.create_event(
                    claim_id, session_id, "JUDGED", self.AGENT_NAME,
                    {
                        "final_confidence": final_score,
                        "verdict": verdict,
                        "consensus_verdict": consensus_result.get("consensus_verdict", ""),
                        "agreement_ratio": consensus_result.get("agreement_ratio", 0),
                        "temporal_relevance": temporal_relevance
                    }
                )
                await db_module.create_claim_event(database, event)
                
                # Update DNA fingerprint
                if claim.get("dna_fingerprint"):
                    claim["dna_fingerprint"] = claim_dna_service.update_fingerprint(
                        claim["dna_fingerprint"], event
                    )
                    await db_module.update_claim(database, claim_id, {
                        "dna_fingerprint": claim["dna_fingerprint"]
                    })
                
                # Emit judgment event
                verdict_emoji = "✅" if verdict == "accepted" else "❌" if verdict == "rejected" else "⚠️"
                await self.emit_event(
                    "claim_judged",
                    f"{verdict_emoji} Verdict: {verdict.upper()} ({final_score:.1f}%) — {claim['text'][:60]}...",
                    to_agent="synthesizer",
                    metadata={
                        "claim_id": claim_id,
                        "verdict": verdict,
                        "confidence": final_score,
                        "consensus_verdict": consensus_result.get("consensus_verdict"),
                        "agreement_ratio": consensus_result.get("agreement_ratio")
                    }
                )
                
                judged_claims.append(claim)
            
            # Update session
            accepted = sum(1 for c in judged_claims if c.get("verdict") == "accepted")
            rejected = sum(1 for c in judged_claims if c.get("verdict") == "rejected")
            uncertain = sum(1 for c in judged_claims if c.get("verdict") == "uncertain")
            
            overall_confidence = (
                sum(c.get("confidence_score", 0) for c in judged_claims) / len(judged_claims)
                if judged_claims else 0
            )
            
            # Detect contradictions
            contradictions = claim_dna_service.detect_contradictions(judged_claims)
            
            await db_module.update_session(database, session_id, {
                "verified_claims": accepted,
                "disputed_claims": rejected,
                "unverified_claims": uncertain,
                "overall_confidence": round(overall_confidence, 1),
                "contradiction_count": len(contradictions),
                "current_agent": "synthesizer"
            })
            
            # Attach contradictions to the data for synthesizer
            for claim in judged_claims:
                claim["contradictions"] = [
                    c for c in contradictions 
                    if c["claim_a_id"] == claim.get("id") or c["claim_b_id"] == claim.get("id")
                ]
            
            await self.complete(
                session_id,
                f"⚖️ Judge completed: {accepted} accepted, {rejected} rejected, "
                f"{uncertain} uncertain. Overall: {overall_confidence:.1f}%"
            )
            
            return judged_claims
            
        except Exception as e:
            await self.error(session_id, str(e))
            raise
        finally:
            await database.close()
    
    async def _run_debate(self, claim: dict, session_id: str) -> dict:
        """Run a debate between Verifier and Devil's Advocate."""
        
        # Build evidence summary
        corr_summary = "\n".join([
            f"- {s.get('snippet', '')[:150]}"
            for s in claim.get("corroborating_sources", [])[:3]
        ]) or "No corroborating evidence found."
        
        counter_args = "\n".join([
            f"- {arg[:150]}" for arg in claim.get("counter_arguments", [])[:3]
        ]) or "No counter-arguments raised."
        
        fallacies = ", ".join(claim.get("logical_fallacies", [])) or "None identified"
        biases = ", ".join(claim.get("bias_flags", [])) or "None identified"
        
        prompt = f"""You are presiding as Judge over a debate about a factual claim.

CLAIM: "{claim['text']}"

VERIFIER'S CASE (Supporting):
{corr_summary}

DEVIL'S ADVOCATE'S CASE (Challenging):
Counter-arguments:
{counter_args}
Logical fallacies identified: {fallacies}
Bias flags: {biases}

As Judge, conduct a {settings.DEBATE_ROUNDS}-round debate analysis and render a verdict.

Respond with ONLY valid JSON:
{{
    "rounds": [
        {{
            "round_number": 1,
            "verifier_argument": {{
                "position": "Summary of verifier's position",
                "evidence": ["key evidence point 1"],
                "confidence": <0-100>
            }},
            "devils_advocate_argument": {{
                "position": "Summary of devil's advocate's position",
                "evidence": ["key counter-point 1"],
                "confidence": <0-100>
            }}
        }}
    ],
    "verdict": {{
        "decision": "accepted" or "rejected" or "uncertain",
        "confidence": <0-100>,
        "reasoning": "Detailed reasoning for the verdict"
    }}
}}"""
        
        result = await llm_service.generate_json(prompt, temperature=0.4)
        
        if isinstance(result, dict) and "rounds" in result:
            return result
        
        # Fallback
        return {
            "rounds": [{
                "round_number": 1,
                "verifier_argument": {
                    "position": "Evidence supports the claim",
                    "evidence": [claim.get("verification_analysis", "")[:200]],
                    "confidence": claim.get("confidence_score", 50)
                },
                "devils_advocate_argument": {
                    "position": "Challenge raised",
                    "evidence": claim.get("counter_arguments", [])[:2],
                    "confidence": 50
                }
            }],
            "verdict": {
                "decision": "uncertain",
                "confidence": claim.get("confidence_score", 50),
                "reasoning": "Insufficient debate data for clear verdict"
            }
        }
    
    def _calculate_final_confidence(self, claim: dict, debate_data: dict, 
                                     consensus_result: dict) -> float:
        """
        Calculate the final confidence score by combining:
        - Current confidence (from verification + challenge)
        - Debate outcome
        - Multi-model consensus
        """
        current = claim.get("confidence_score", 50)
        
        # Debate weight (30%)
        debate_confidence = debate_data.get("verdict", {}).get("confidence", 50)
        
        # Consensus weight (40%)
        consensus_confidence = consensus_result.get("consensus_confidence", 50)
        agreement_boost = consensus_result.get("agreement_ratio", 0.5) * 10
        
        # Source credibility weight (30%)
        source_quality = self._calculate_source_quality(claim)
        
        # Weighted combination
        final = (
            current * 0.20 +
            debate_confidence * 0.25 +
            consensus_confidence * 0.35 +
            source_quality * 0.20 +
            agreement_boost
        )
        
        return round(max(0, min(100, final)), 1)
    
    def _calculate_source_quality(self, claim: dict) -> float:
        """Calculate average source quality score."""
        sources = claim.get("sources", []) + claim.get("corroborating_sources", [])
        if not sources:
            return 30
        
        scores = [s.get("credibility_score", 50) for s in sources]
        return sum(scores) / len(scores)
    
    def _determine_verdict(self, confidence: float) -> str:
        """Determine verdict based on final confidence score."""
        if confidence >= 70:
            return "accepted"
        elif confidence <= 35:
            return "rejected"
        else:
            return "uncertain"
    
    def _calculate_temporal_relevance(self, claim: dict) -> float:
        """
        Calculate temporal relevance of a claim.
        Claims about recent events get a boost, older claims get a penalty.
        """
        # Default to high relevance (we don't have publication dates for all sources)
        relevance = 1.0
        
        text = claim.get("text", "").lower()
        
        # Check for temporal indicators
        import re
        current_year = datetime.now().year
        
        # Find year references
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
        if years:
            most_recent = max(int(y) for y in years)
            years_ago = current_year - most_recent
            
            if years_ago <= 1:
                relevance = 1.0  # Very recent
            elif years_ago <= 3:
                relevance = 0.9
            elif years_ago <= 5:
                relevance = 0.8
            elif years_ago <= 10:
                relevance = 0.6
            else:
                relevance = 0.4
        
        # Apply decay formula: e^(-rate * days)
        # Since we can't always determine exact age, use a conservative estimate
        decay_rate = settings.CONFIDENCE_DECAY_RATE
        
        return round(relevance, 2)


# Singleton instance
judge_agent = JudgeAgent()
