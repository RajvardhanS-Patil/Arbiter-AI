"""
Arbiter AI — Devil's Advocate Agent
Adversarial agent that actively tries to disprove every claim.
Generates counter-arguments, finds logical fallacies, and detects biases.
"""

import uuid
from agents.base_agent import BaseAgent
from services.llm_service import llm_service
from services.search_service import search_service
from services.claim_dna_service import claim_dna_service
import database as db_module


class DevilsAdvocateAgent(BaseAgent):
    """
    😈 The Devil's Advocate
    Actively tries to DISPROVE every claim. Generates counter-arguments
    and identifies weaknesses in the evidence.
    """
    
    AGENT_NAME = "devils_advocate"
    AGENT_EMOJI = "😈"
    
    async def process(self, session_id: str, data: list[dict]) -> list[dict]:
        """
        Challenge each claim with adversarial analysis.
        
        Args:
            data: List of verified claims from the Verifier
            
        Returns:
            Claims enriched with adversarial challenges
        """
        claims = data
        await self.start(session_id)
        
        database = await db_module.get_db()
        
        try:
            challenged_claims = []
            
            for i, claim in enumerate(claims):
                await self.emit_progress(
                    i + 1, len(claims),
                    f"😈 Challenging: {claim['text'][:60]}..."
                )
                
                claim_id = claim.get("id", "")
                
                # Step 1: Generate adversarial analysis via LLM
                challenge = await self._generate_challenge(claim)
                
                # Step 2: Search for counter-evidence
                counter_results = await search_service.search_web(
                    f"why is this wrong OR criticism of: {claim['text'][:80]}",
                    max_results=3
                )
                
                # Add counter-evidence snippets to arguments
                for result in counter_results:
                    if result.get("snippet"):
                        challenge["counter_arguments"].append(
                            f"[{result.get('title', 'Source')}]: {result['snippet'][:200]}"
                        )
                
                # Step 3: Update claim with challenge data
                claim["counter_arguments"] = challenge.get("counter_arguments", [])
                claim["logical_fallacies"] = challenge.get("logical_fallacies", [])
                claim["bias_flags"] = challenge.get("bias_flags", [])
                
                # Adjust confidence based on challenge strength
                challenge_strength = challenge.get("challenge_strength", 0)
                confidence_penalty = min(25, challenge_strength * 5)
                claim["confidence_score"] = max(0, 
                    claim.get("confidence_score", 50) - confidence_penalty
                )
                
                # Update in database
                await db_module.update_claim(database, claim_id, {
                    "counter_arguments": claim["counter_arguments"],
                    "logical_fallacies": claim["logical_fallacies"],
                    "bias_flags": claim["bias_flags"],
                    "confidence_score": claim["confidence_score"]
                })
                
                # Create CHALLENGED genealogy event
                event = claim_dna_service.create_event(
                    claim_id, session_id, "CHALLENGED", self.AGENT_NAME,
                    {
                        "counter_arguments_count": len(claim["counter_arguments"]),
                        "fallacies_found": len(claim["logical_fallacies"]),
                        "biases_found": len(claim["bias_flags"]),
                        "challenge_strength": challenge_strength,
                        "confidence_penalty": f"-{confidence_penalty}"
                    }
                )
                await db_module.create_claim_event(database, event)
                
                # Emit challenge event
                challenge_severity = "🔴" if challenge_strength > 3 else "🟡" if challenge_strength > 1 else "🟢"
                await self.emit_event(
                    "claim_challenged",
                    f"{challenge_severity} Challenge ({challenge_strength}/5): {claim['text'][:60]}...",
                    to_agent="judge",
                    metadata={
                        "claim_id": claim_id,
                        "challenge_strength": challenge_strength,
                        "counter_arguments": len(claim["counter_arguments"]),
                        "fallacies": len(claim["logical_fallacies"]),
                        "biases": len(claim["bias_flags"])
                    }
                )
                
                challenged_claims.append(claim)
            
            # Update session
            await db_module.update_session(database, session_id, {
                "current_agent": "judge"
            })
            
            await self.complete(
                session_id,
                f"😈 Devil's Advocate completed: Challenged {len(claims)} claims"
            )
            
            return challenged_claims
            
        except Exception as e:
            await self.error(session_id, str(e))
            raise
        finally:
            await database.close()
    
    async def _generate_challenge(self, claim: dict) -> dict:
        """Generate adversarial challenge for a claim using LLM."""
        
        sources_info = ""
        for s in claim.get("sources", [])[:3]:
            sources_info += f"\n- {s.get('title', 'Unknown')} ({s.get('credibility_tier', 'UNKNOWN')})"
        
        prompt = f"""You are a Devil's Advocate — your job is to critically analyze and challenge this claim. Try to find weaknesses, flaws, and reasons it might be wrong.

CLAIM: "{claim['text']}"
CURRENT STATUS: {claim.get('verification_status', 'unverified')}
SOURCES: {sources_info or 'No source details available'}

Analyze the claim for:
1. Counter-arguments: What arguments could be made AGAINST this claim?
2. Logical fallacies: Does the claim or its supporting evidence contain any logical fallacies?
3. Bias flags: Are there potential biases in the sources or framing?
4. Challenge strength: How strong is your case against this claim? (1=weak, 5=strong)

Respond with ONLY valid JSON:
{{
    "counter_arguments": ["argument 1", "argument 2"],
    "logical_fallacies": ["fallacy 1 if any"],
    "bias_flags": ["bias 1 if any"],
    "challenge_strength": <number 1-5>,
    "summary": "Brief summary of your challenge"
}}"""
        
        result = await llm_service.generate_json(prompt, temperature=0.5)
        
        if isinstance(result, dict):
            return {
                "counter_arguments": result.get("counter_arguments", [])[:5],
                "logical_fallacies": result.get("logical_fallacies", [])[:3],
                "bias_flags": result.get("bias_flags", [])[:3],
                "challenge_strength": min(5, max(1, result.get("challenge_strength", 2))),
                "summary": result.get("summary", "")
            }
        
        return {
            "counter_arguments": [],
            "logical_fallacies": [],
            "bias_flags": [],
            "challenge_strength": 2,
            "summary": "Unable to generate challenge"
        }


# Singleton instance
devils_advocate_agent = DevilsAdvocateAgent()
