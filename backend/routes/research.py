"""
Arbiter AI — Research Routes
Handles endpoints starting and monitoring research sessions,
claims, sources, debates, and contradictions.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import (
    ResearchRequest, ResearchStartResponse, SessionStatusResponse,
    ClaimsListResponse, ClaimResponse, SourceResponse,
    DebateResponse, ContradictionsResponse, SessionProgress
)
from agents.orchestrator import orchestrator_agent
import database as db_module
import uuid
import asyncio

router = APIRouter()

# Global dict of active session tasks to allow status checking or cancellation
active_tasks = {}

async def run_pipeline_wrapper(session_id: str, query: str, depth: str, max_claims: int, enable_debate: bool, enable_multi_model: bool):
    """Async wrapper to run the pipeline in background."""
    try:
        await orchestrator_agent.run_pipeline(
            session_id=session_id,
            query=query,
            depth=depth,
            max_claims=max_claims,
            enable_debate=enable_debate,
            enable_multi_model=enable_multi_model
        )
    except Exception as e:
        print(f"Error in pipeline background run for session {session_id}: {e}")
    finally:
        active_tasks.pop(session_id, None)


@router.post("/research", response_model=ResearchStartResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new research session in the background."""
    session_id = str(uuid.uuid4())
    
    # Save the session to the DB as pending
    db = await db_module.get_db()
    try:
        await db_module.create_session(db, {
            "id": session_id,
            "query": request.query,
            "depth": request.depth
        })
    finally:
        await db.close()
    
    # Run pipeline in background
    task = asyncio.create_task(
        run_pipeline_wrapper(
            session_id=session_id,
            query=request.query,
            depth=request.depth,
            max_claims=request.max_claims,
            enable_debate=request.enable_debate,
            enable_multi_model=request.enable_multi_model
        )
    )
    active_tasks[session_id] = task
    
    websocket_url = f"ws://localhost:8000/ws/session/{session_id}"
    
    return ResearchStartResponse(
        session_id=session_id,
        status="started",
        message="Research pipeline initiated successfully",
        websocket_url=websocket_url
    )


@router.get("/research/{session_id}", response_model=SessionStatusResponse)
async def get_research_status(session_id: str):
    """Get the current progress status of a research session."""
    db = await db_module.get_db()
    try:
        session = await db_module.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Calculate elapsed time
        from datetime import datetime
        import pytz
        
        created_at_str = session.get("created_at", "")
        # Remove 'Z' if present, replace space with T
        created_at_str = created_at_str.replace(" ", "T")
        try:
            created_at = datetime.fromisoformat(created_at_str)
            elapsed = (datetime.utcnow() - created_at).total_seconds()
        except Exception:
            elapsed = 0.0
            
        if session.get("status") == "completed" or session.get("status") == "failed":
            elapsed = session.get("processing_time") or elapsed

        # Get agent progress
        agent_statuses = orchestrator_agent.get_agent_statuses()
        progress = SessionProgress(
            investigator=agent_statuses.get("investigator", {}).get("status", "pending"),
            verifier=agent_statuses.get("verifier", {}).get("status", "pending"),
            devils_advocate=agent_statuses.get("devils_advocate", {}).get("status", "pending"),
            judge=agent_statuses.get("judge", {}).get("status", "pending"),
            synthesizer=agent_statuses.get("synthesizer", {}).get("status", "pending")
        )
        
        return SessionStatusResponse(
            session_id=session_id,
            query=session["query"],
            status=session["status"],
            current_agent=session.get("current_agent"),
            progress=progress,
            claims_found=session.get("total_claims") or 0,
            claims_verified=session.get("verified_claims") or 0,
            elapsed_time=round(elapsed, 1),
            overall_confidence=session.get("overall_confidence")
        )
    finally:
        await db.close()


@router.get("/research/{session_id}/claims", response_model=ClaimsListResponse)
async def get_session_claims(session_id: str):
    """Retrieve all claims extracted during a session."""
    db = await db_module.get_db()
    try:
        session = await db_module.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        claims_rows = await db_module.get_claims_by_session(db, session_id)
        claims_list = []
        
        verified_count = 0
        disputed_count = 0
        unverified_count = 0
        
        for row in claims_rows:
            claim_id = row["id"]
            
            # Count statuses
            status = row.get("verification_status", "unverified")
            if status == "verified":
                verified_count += 1
            elif status == "disputed":
                disputed_count += 1
            else:
                unverified_count += 1
                
            # Get sources for this claim
            sources_rows = await db_module.get_sources_by_claim(db, claim_id)
            sources = [SourceResponse(**s) for s in sources_rows]
            
            # Get genealogy events
            events_rows = await db_module.get_claim_events(db, claim_id)
            import json
            genealogy = []
            for ev in events_rows:
                details = ev.get("details", "{}")
                if isinstance(details, str):
                    try:
                        details = json.loads(details)
                    except Exception:
                        details = {}
                genealogy.append({
                    "id": ev["id"],
                    "event_type": ev["event_type"],
                    "agent": ev.get("agent") or "",
                    "details": details,
                    "timestamp": ev.get("timestamp")
                })
            
            # Convert list fields
            import json
            def load_list_field(field_val):
                if not field_val:
                    return []
                if isinstance(field_val, list):
                    return field_val
                try:
                    return json.loads(field_val)
                except Exception:
                    return []
            
            counter_arguments = load_list_field(row.get("counter_arguments"))
            logical_fallacies = load_list_field(row.get("logical_fallacies"))
            bias_flags = load_list_field(row.get("bias_flags"))
            
            claims_list.append(ClaimResponse(
                id=claim_id,
                text=row["text"],
                category=row.get("category") or "general",
                verification_status=status,
                confidence_score=row.get("confidence_score") or 0.0,
                verdict=row.get("verdict"),
                judge_reasoning=row.get("judge_reasoning"),
                dna_fingerprint=row.get("dna_fingerprint"),
                temporal_relevance=row.get("temporal_relevance") or 1.0,
                counter_arguments=counter_arguments,
                logical_fallacies=logical_fallacies,
                bias_flags=bias_flags,
                sources=sources,
                genealogy=genealogy,
                created_at=row.get("created_at"),
                last_verified=row.get("last_verified")
            ))
            
        return ClaimsListResponse(
            claims=claims_list,
            total=len(claims_list),
            verified_count=verified_count,
            disputed_count=disputed_count,
            unverified_count=unverified_count
        )
    finally:
        await db.close()


@router.get("/research/{session_id}/contradictions", response_model=ContradictionsResponse)
async def get_session_contradictions(session_id: str):
    """Retrieve any contradictions detected among the claims."""
    db = await db_module.get_db()
    try:
        session = await db_module.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        claims_rows = await db_module.get_claims_by_session(db, session_id)
        # We need to construct full claim structures to check contradictions
        claims_for_analysis = []
        for r in claims_rows:
            sources_rows = await db_module.get_sources_by_claim(db, r["id"])
            claims_for_analysis.append({
                "id": r["id"],
                "text": r["text"],
                "category": r.get("category") or "general",
                "sources": [{"url": s["url"]} for s in sources_rows]
            })
            
        from services.claim_dna_service import claim_dna_service
        contradictions = claim_dna_service.detect_contradictions(claims_for_analysis)
        
        # Calculate topic conflict densities
        from collections import Counter
        topics = [c["category"] for c in claims_for_analysis]
        topic_counts = Counter(topics)
        
        topic_conflicts_map = {}
        for contra in contradictions:
            claim_id = contra["claim_a_id"]
            # Find claim category
            cat = "general"
            for c in claims_for_analysis:
                if c["id"] == claim_id:
                    cat = c["category"]
                    break
            
            if cat not in topic_conflicts_map:
                topic_conflicts_map[cat] = {"score_sum": 0.0, "count": 0}
            topic_conflicts_map[cat]["score_sum"] += contra["conflict_score"]
            topic_conflicts_map[cat]["count"] += 1
            
        topic_conflicts = []
        for cat, data in topic_conflicts_map.items():
            density = data["score_sum"] / topic_counts[cat] if topic_counts[cat] > 0 else 0.0
            topic_conflicts.append({
                "topic": cat.replace("_", " ").title(),
                "conflict_density": round(density, 2),
                "claim_count": topic_counts[cat]
            })
            
        avg_score = (sum(c["conflict_score"] for c in contradictions) / len(contradictions)) if contradictions else 0.0
        
        return ContradictionsResponse(
            session_id=session_id,
            contradiction_matrix=contradictions,
            topic_conflicts=topic_conflicts,
            total_contradictions=len(contradictions),
            average_conflict_score=round(avg_score, 2)
        )
    finally:
        await db.close()


@router.get("/research/{session_id}/sources", response_model=list[SourceResponse])
async def get_session_sources(session_id: str):
    """Retrieve all sources collected during the session."""
    db = await db_module.get_db()
    try:
        session = await db_module.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        sources_rows = await db_module.get_sources_by_session(db, session_id)
        return [SourceResponse(**s) for s in sources_rows]
    finally:
        await db.close()


@router.get("/research/{session_id}/debate", response_model=list[DebateResponse])
async def get_session_debates(session_id: str):
    """Retrieve adversarial debate logs for the claims."""
    db = await db_module.get_db()
    try:
        session = await db_module.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        debates_rows = await db_module.get_debates_by_session(db, session_id)
        return [DebateResponse(**d) for d in debates_rows]
    finally:
        await db.close()
