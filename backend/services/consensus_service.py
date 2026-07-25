"""
Arbiter AI — Consensus Service
Multi-model consensus voting for claim verification.
Uses multiple LLM providers as a "jury" to vote on claim validity.
"""

import uuid
from services.llm_service import llm_service
from config import settings


class ConsensusService:
    """
    Multi-model consensus engine.
    Sends claims to multiple AI providers and aggregates their verdicts.
    """
    
    async def evaluate_claim(self, claim_text: str, evidence_for: list[str] = None,
                             evidence_against: list[str] = None,
                             session_id: str = "", claim_id: str = "") -> dict:
        """
        Submit a claim to all available models for consensus evaluation.
        
        Returns:
        {
            "votes": [...],
            "consensus_verdict": "verified|disputed|uncertain",
            "consensus_confidence": float,
            "agreement_ratio": float,
            "details": str
        }
        """
        # Build the evaluation prompt
        prompt = self._build_evaluation_prompt(
            claim_text, evidence_for or [], evidence_against or []
        )
        
        system_prompt = """You are a fact-checking AI judge. Your job is to evaluate whether a claim is factually accurate based on the provided evidence. Be objective, analytical, and precise. Consider the quality and quantity of evidence on both sides."""
        
        # Get votes from all available models
        if settings.ENABLE_MULTI_MODEL and len(llm_service.available_providers) >= 2:
            votes = await llm_service.multi_model_consensus(prompt, system_prompt)
        else:
            # Single model fallback
            votes = await llm_service.multi_model_consensus(prompt, system_prompt)
        
        # Add IDs to votes
        for vote in votes:
            vote["id"] = str(uuid.uuid4())
            vote["claim_id"] = claim_id
            vote["session_id"] = session_id
        
        # Aggregate consensus
        consensus = self._aggregate_votes(votes)
        
        return {
            "votes": votes,
            "consensus_verdict": consensus["verdict"],
            "consensus_confidence": consensus["confidence"],
            "agreement_ratio": consensus["agreement_ratio"],
            "details": consensus["details"]
        }
    
    def _build_evaluation_prompt(self, claim_text: str, evidence_for: list[str],
                                  evidence_against: list[str]) -> str:
        """Build the evaluation prompt for models."""
        prompt = f"""Evaluate the following claim for factual accuracy:

CLAIM: "{claim_text}"

"""
        if evidence_for:
            prompt += "SUPPORTING EVIDENCE:\n"
            for i, e in enumerate(evidence_for, 1):
                prompt += f"{i}. {e}\n"
            prompt += "\n"
        
        if evidence_against:
            prompt += "OPPOSING EVIDENCE:\n"
            for i, e in enumerate(evidence_against, 1):
                prompt += f"{i}. {e}\n"
            prompt += "\n"
        
        prompt += """Based on the evidence provided, evaluate this claim.

Consider:
1. Is the claim supported by credible evidence?
2. Are there strong counter-arguments?
3. Is the claim specific enough to verify?
4. Could the claim be partially true?

Respond with ONLY valid JSON:
{
    "verdict": "verified" or "disputed" or "uncertain",
    "confidence": <number 0-100>,
    "reasoning": "<brief explanation of your judgment>"
}"""
        
        return prompt
    
    def _aggregate_votes(self, votes: list[dict]) -> dict:
        """
        Aggregate votes from multiple models into a consensus.
        Uses weighted majority voting.
        """
        if not votes:
            return {
                "verdict": "uncertain",
                "confidence": 50,
                "agreement_ratio": 0,
                "details": "No votes received"
            }
        
        # Count verdicts
        verdict_counts = {"verified": 0, "disputed": 0, "uncertain": 0}
        total_confidence = 0
        valid_votes = 0
        
        for vote in votes:
            verdict = vote.get("verdict", "uncertain").lower()
            if verdict not in verdict_counts:
                verdict = "uncertain"
            verdict_counts[verdict] += 1
            total_confidence += vote.get("confidence", 50)
            valid_votes += 1
        
        if valid_votes == 0:
            return {
                "verdict": "uncertain",
                "confidence": 50,
                "agreement_ratio": 0,
                "details": "No valid votes"
            }
        
        # Determine majority verdict
        majority_verdict = max(verdict_counts, key=verdict_counts.get)
        majority_count = verdict_counts[majority_verdict]
        
        # Calculate agreement ratio
        agreement_ratio = majority_count / valid_votes
        
        # Calculate average confidence
        avg_confidence = total_confidence / valid_votes
        
        # Adjust confidence based on agreement
        # High agreement boosts confidence, low agreement reduces it
        if agreement_ratio == 1.0:
            adjusted_confidence = avg_confidence * 1.1  # Boost for unanimous
        elif agreement_ratio >= 0.5:
            adjusted_confidence = avg_confidence * agreement_ratio
        else:
            adjusted_confidence = avg_confidence * 0.5  # Penalize low agreement
        
        adjusted_confidence = max(0, min(100, adjusted_confidence))
        
        # Build details
        details_parts = []
        for verdict, count in verdict_counts.items():
            if count > 0:
                details_parts.append(f"{count} model(s) voted '{verdict}'")
        details = "; ".join(details_parts)
        
        return {
            "verdict": majority_verdict,
            "confidence": round(adjusted_confidence, 1),
            "agreement_ratio": round(agreement_ratio, 2),
            "details": details
        }


# Singleton instance
consensus_service = ConsensusService()
