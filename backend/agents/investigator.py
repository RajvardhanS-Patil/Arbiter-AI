"""
Arbiter AI — Investigator Agent
The first agent in the pipeline. Researches a topic by searching
multiple sources and extracting atomic claims with citations.
"""

import uuid
import json
from datetime import datetime
from agents.base_agent import BaseAgent
from services.llm_service import llm_service
from services.search_service import search_service
from services.credibility_service import credibility_service
from services.claim_dna_service import claim_dna_service
from config import settings
import database as db_module


class InvestigatorAgent(BaseAgent):
    """
    🔍 The Investigator
    Receives a query, searches multiple sources, and extracts atomic claims.
    """
    
    AGENT_NAME = "investigator"
    AGENT_EMOJI = "🔍"
    
    async def process(self, session_id: str, data: dict) -> list[dict]:
        """
        Research a topic and extract claims.
        
        Args:
            data: {"query": str, "depth": str, "max_claims": int}
            
        Returns:
            List of claim dicts with source citations
        """
        query = data["query"]
        depth = data.get("depth", "standard")
        max_claims = data.get("max_claims", settings.MAX_CLAIMS_PER_QUERY)
        
        await self.start(session_id)
        
        database = await db_module.get_db()
        
        try:
            # Step 1: Break query into sub-questions
            await self.emit_event(
                "agent_progress",
                f"🔍 Breaking down research topic: '{query}'",
                to_agent="verifier",
                metadata={"step": "decompose_query"}
            )
            
            sub_questions = await self._decompose_query(query, depth)
            
            await self.emit_event(
                "agent_message",
                f"📋 Generated {len(sub_questions)} research sub-questions",
                to_agent="verifier",
                metadata={"sub_questions": sub_questions}
            )
            
            # Step 2: Search for each sub-question
            all_search_results = []
            for i, sq in enumerate(sub_questions):
                await self.emit_progress(
                    i + 1, len(sub_questions),
                    f"🔎 Searching: {sq[:60]}..."
                )
                
                results = await search_service.comprehensive_search(sq)
                all_search_results.extend(results)
            
            # Deduplicate by URL
            seen_urls = set()
            unique_results = []
            for r in all_search_results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(r)
            
            await self.emit_event(
                "agent_message",
                f"📚 Found {len(unique_results)} unique sources across {len(sub_questions)} searches",
                to_agent="verifier",
                metadata={"total_sources": len(unique_results)}
            )
            
            # Step 3: Score source credibility
            for result in unique_results:
                cred = credibility_service.score_source(
                    result.get("url", ""),
                    result.get("title", ""),
                    result.get("snippet", "")
                )
                result["credibility_score"] = cred["credibility_score"]
                result["credibility_tier"] = cred["credibility_tier"]
            
            # Step 4: Extract claims from sources using LLM
            await self.emit_event(
                "agent_progress",
                "🧠 Extracting and analyzing claims from sources...",
                metadata={"step": "extract_claims"}
            )
            
            claims = await self._extract_claims(query, unique_results, max_claims)
            
            # Step 5: Save claims and sources to database
            for claim in claims:
                claim["session_id"] = session_id
                claim["id"] = str(uuid.uuid4())
                claim["verification_status"] = "unverified"
                claim["confidence_score"] = 30  # Initial low confidence
                
                # Generate initial DNA fingerprint
                source_urls = [s.get("url", "") for s in claim.get("sources", [])]
                claim["dna_fingerprint"] = claim_dna_service.generate_fingerprint(
                    claim["text"], source_urls
                )
                
                # Save claim to DB
                await db_module.create_claim(database, claim)
                
                # Save sources for this claim
                for source in claim.get("sources", []):
                    source_record = {
                        "id": str(uuid.uuid4()),
                        "claim_id": claim["id"],
                        "session_id": session_id,
                        "url": source.get("url", ""),
                        "title": source.get("title", ""),
                        "domain": source.get("domain", ""),
                        "credibility_score": source.get("credibility_score", 50),
                        "credibility_tier": source.get("credibility_tier", "UNKNOWN"),
                        "snippet": source.get("snippet", ""),
                        "relationship": "original"
                    }
                    await db_module.create_source(database, source_record)
                
                # Create BORN genealogy event
                event = claim_dna_service.create_event(
                    claim["id"], session_id, "BORN", self.AGENT_NAME,
                    {"source_count": len(claim.get("sources", [])),
                     "initial_confidence": claim["confidence_score"]}
                )
                await db_module.create_claim_event(database, event)
                
                # Emit claim_created event
                await self.emit_event(
                    "claim_created",
                    f"📝 New claim: {claim['text'][:80]}...",
                    to_agent="verifier",
                    metadata={
                        "claim_id": claim["id"],
                        "source_count": len(claim.get("sources", [])),
                        "category": claim.get("category", "general")
                    }
                )
            
            # Update session stats
            await db_module.update_session(database, session_id, {
                "total_claims": len(claims),
                "total_sources": len(unique_results),
                "current_agent": "verifier"
            })
            
            await self.complete(
                session_id,
                f"🔍 Investigator completed: {len(claims)} claims from {len(unique_results)} sources"
            )
            
            return claims
            
        except Exception as e:
            await self.error(session_id, str(e))
            raise
        finally:
            await database.close()
    
    async def _decompose_query(self, query: str, depth: str) -> list[str]:
        """Break a query into sub-questions for comprehensive research."""
        depth_config = {
            "quick": 3,
            "standard": 5,
            "deep": 8
        }
        num_questions = depth_config.get(depth, 5)
        
        prompt = f"""Given this research topic, generate {num_questions} specific search queries that would help thoroughly investigate it. Each query should cover a different angle or aspect of the topic.

Topic: "{query}"

Generate exactly {num_questions} search queries. Respond with ONLY a JSON array of strings:
["query 1", "query 2", ...]"""
        
        result = await llm_service.generate_json(prompt)
        
        if isinstance(result, list):
            return result[:num_questions]
        
        # Fallback: use the original query plus variations
        return [query, f"{query} latest research", f"{query} facts and statistics"]
    
    async def _extract_claims(self, query: str, sources: list[dict], 
                              max_claims: int) -> list[dict]:
        """Extract atomic claims from search results using LLM."""
        
        # Build source context for LLM
        source_context = ""
        for i, s in enumerate(sources[:12], 1):  # Limit to top 12 sources
            source_context += f"\n--- Source {i} ---\n"
            source_context += f"Title: {s.get('title', 'Unknown')}\n"
            source_context += f"URL: {s.get('url', '')}\n"
            source_context += f"Credibility: {s.get('credibility_tier', 'UNKNOWN')} ({s.get('credibility_score', 0)})\n"
            source_context += f"Content: {s.get('snippet', s.get('summary', ''))}\n"
        
        prompt = f"""You are a research analyst. Extract specific, atomic, verifiable factual claims from the following sources about: "{query}"

Rules:
1. Each claim must be a single, specific, verifiable statement
2. Each claim must be attributable to at least one source
3. Avoid opinions — focus on factual statements
4. Include numbers, dates, and specific details where available
5. Assign a category to each claim (e.g., "statistics", "history", "science", "policy", "economics")
6. Extract at most {max_claims} claims, prioritizing the most important ones

Sources:
{source_context}

Respond with ONLY a JSON array of claim objects:
[
  {{
    "text": "The specific factual claim statement",
    "category": "topic category",
    "source_indices": [1, 3]
  }}
]

Extract the most important and verifiable claims. Output ONLY the JSON array."""
        
        result = await llm_service.generate_json(prompt)
        
        claims = []
        if isinstance(result, list):
            for item in result[:max_claims]:
                if isinstance(item, dict) and "text" in item:
                    # Map source indices to actual source data
                    source_indices = item.get("source_indices", [])
                    claim_sources = []
                    for idx in source_indices:
                        if 1 <= idx <= len(sources):
                            s = sources[idx - 1]
                            claim_sources.append({
                                "url": s.get("url", ""),
                                "title": s.get("title", ""),
                                "domain": s.get("domain", ""),
                                "snippet": s.get("snippet", ""),
                                "credibility_score": s.get("credibility_score", 50),
                                "credibility_tier": s.get("credibility_tier", "UNKNOWN")
                            })
                    
                    # If no source indices provided, assign the first available source
                    if not claim_sources and sources:
                        s = sources[0]
                        claim_sources.append({
                            "url": s.get("url", ""),
                            "title": s.get("title", ""),
                            "domain": s.get("domain", ""),
                            "snippet": s.get("snippet", ""),
                            "credibility_score": s.get("credibility_score", 50),
                            "credibility_tier": s.get("credibility_tier", "UNKNOWN")
                        })
                    
                    claims.append({
                        "text": item["text"],
                        "category": item.get("category", "general"),
                        "sources": claim_sources
                    })
        
        return claims


# Singleton instance
investigator_agent = InvestigatorAgent()
