"""
Arbiter AI — Claim DNA Service
Generates unique fingerprints for claims and tracks their lifecycle events.
Each claim gets a "DNA" — a hash encoding its verification history.
"""

import hashlib
import json
import uuid
from datetime import datetime


class ClaimDNAService:
    """Manages claim DNA fingerprinting and genealogy tracking."""
    
    def generate_fingerprint(self, claim_text: str, sources: list[str] = None, 
                             verification_events: list[dict] = None) -> str:
        """
        Generate a unique DNA fingerprint for a claim.
        The fingerprint encodes the claim's text, sources, and verification history.
        """
        # Build the DNA string from claim components
        dna_components = [
            claim_text.strip().lower(),
            json.dumps(sorted(sources or []), sort_keys=True),
            json.dumps(verification_events or [], sort_keys=True, default=str)
        ]
        
        dna_string = "|".join(dna_components)
        
        # Generate SHA-256 hash and take first 16 chars
        fingerprint = hashlib.sha256(dna_string.encode('utf-8')).hexdigest()[:16]
        
        return fingerprint
    
    def create_event(self, claim_id: str, session_id: str, event_type: str, 
                     agent: str, details: dict = None) -> dict:
        """
        Create a genealogy event for a claim.
        
        Event types:
        - BORN: Claim first extracted
        - SOURCED: Sources attached
        - VERIFIED: Cross-verified
        - CHALLENGED: Attacked by Devil's Advocate
        - DEFENDED: Successfully defended
        - MUTATED: Claim text refined
        - JUDGED: Final verdict issued
        - ACCEPTED: Final acceptance
        - REJECTED: Final rejection
        """
        return {
            "id": str(uuid.uuid4()),
            "claim_id": claim_id,
            "session_id": session_id,
            "event_type": event_type,
            "agent": agent,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def update_fingerprint(self, current_fingerprint: str, new_event: dict) -> str:
        """
        Update a claim's fingerprint when a new event occurs.
        The new fingerprint incorporates the previous one + new event.
        """
        update_string = f"{current_fingerprint}|{json.dumps(new_event, sort_keys=True, default=str)}"
        new_fingerprint = hashlib.sha256(update_string.encode('utf-8')).hexdigest()[:16]
        return new_fingerprint
    
    def calculate_claim_similarity(self, claim_a: str, claim_b: str) -> float:
        """
        Calculate semantic similarity between two claims using word overlap.
        Returns a score between 0 and 1.
        This is a lightweight NLP approach — no external models needed.
        """
        # Tokenize and normalize
        words_a = set(self._tokenize(claim_a))
        words_b = set(self._tokenize(claim_b))
        
        if not words_a or not words_b:
            return 0.0
        
        # Jaccard similarity
        intersection = words_a & words_b
        union = words_a | words_b
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def detect_contradictions(self, claims: list[dict]) -> list[dict]:
        """
        Detect potential contradictions between claims.
        Uses keyword-based contradiction detection.
        Returns list of contradiction pairs with conflict scores.
        """
        contradictions = []
        
        # Contradiction indicator words
        negation_words = {"not", "no", "never", "neither", "nor", "false", 
                         "incorrect", "wrong", "unlikely", "impossible",
                         "decrease", "decline", "reduce", "lower", "less",
                         "fail", "unable", "cannot", "shouldn't", "won't"}
        
        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                claim_a = claims[i]
                claim_b = claims[j]
                
                text_a = claim_a.get("text", "").lower()
                text_b = claim_b.get("text", "").lower()
                
                # Check topic similarity first (must be about same topic)
                similarity = self.calculate_claim_similarity(text_a, text_b)
                
                if similarity < 0.15:  # Too different topics — skip
                    continue
                
                # Check for contradiction signals
                words_a = set(self._tokenize(text_a))
                words_b = set(self._tokenize(text_b))
                
                negations_a = words_a & negation_words
                negations_b = words_b & negation_words
                
                # If one has negation and other doesn't, on similar topic → contradiction
                conflict_score = 0.0
                conflict_type = "potential_contradiction"
                
                if bool(negations_a) != bool(negations_b) and similarity > 0.25:
                    conflict_score = similarity * 0.8 + 0.2
                    conflict_type = "negation_contradiction"
                elif similarity > 0.5 and self._has_numeric_conflict(text_a, text_b):
                    conflict_score = 0.7
                    conflict_type = "numeric_contradiction"
                elif similarity > 0.3:
                    # Moderate similarity but different enough to be worth flagging
                    conflict_score = similarity * 0.5
                    conflict_type = "potential_contradiction"
                
                if conflict_score > 0.3:
                    contradictions.append({
                        "claim_a_id": claim_a.get("id", ""),
                        "claim_a_text": claim_a.get("text", ""),
                        "claim_b_id": claim_b.get("id", ""),
                        "claim_b_text": claim_b.get("text", ""),
                        "conflict_score": round(conflict_score, 2),
                        "conflict_type": conflict_type,
                        "sources_a": [s.get("url", "") for s in claim_a.get("sources", [])],
                        "sources_b": [s.get("url", "") for s in claim_b.get("sources", [])]
                    })
        
        # Sort by conflict score descending
        contradictions.sort(key=lambda x: x["conflict_score"], reverse=True)
        
        return contradictions
    
    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization — split into words, remove punctuation."""
        import re
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', '', text.lower())
        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                     "being", "have", "has", "had", "do", "does", "did", "will",
                     "would", "could", "should", "may", "might", "can", "shall",
                     "to", "of", "in", "for", "on", "with", "at", "by", "from",
                     "as", "into", "through", "during", "before", "after", "and",
                     "but", "or", "if", "than", "that", "this", "it", "its"}
        words = [w for w in text.split() if w and w not in stop_words and len(w) > 2]
        return words
    
    def _has_numeric_conflict(self, text_a: str, text_b: str) -> bool:
        """Check if two texts have conflicting numeric values."""
        import re
        
        # Extract numbers with context
        pattern = r'(\d+\.?\d*)\s*(%|percent|million|billion|trillion|degrees?|celsius|fahrenheit|years?|months?|days?)?'
        
        nums_a = re.findall(pattern, text_a)
        nums_b = re.findall(pattern, text_b)
        
        if not nums_a or not nums_b:
            return False
        
        # Check if same unit but different number
        for num_a, unit_a in nums_a:
            for num_b, unit_b in nums_b:
                if unit_a and unit_a == unit_b:
                    try:
                        val_a = float(num_a)
                        val_b = float(num_b)
                        # More than 20% difference
                        if val_a > 0 and abs(val_a - val_b) / val_a > 0.2:
                            return True
                    except ValueError:
                        pass
        
        return False
    
    def categorize_claims(self, claims: list[dict]) -> dict[str, list[str]]:
        """
        Group claims by topic category.
        Returns {category: [claim_ids]}.
        """
        # Simple keyword-based categorization
        categories = {}
        
        for claim in claims:
            text = claim.get("text", "").lower()
            category = claim.get("category", "general")
            
            if category not in categories:
                categories[category] = []
            categories[category].append(claim.get("id", ""))
        
        return categories


# Singleton instance
claim_dna_service = ClaimDNAService()
