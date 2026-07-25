"""
Arbiter AI — Sessions Routes
Handles listing history of all sessions and deleting sessions.
"""

from fastapi import APIRouter, HTTPException, Query
from models.schemas import SessionListResponse, SessionListItem
import database as db_module

router = APIRouter()

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieve all past research sessions."""
    db = await db_module.get_db()
    try:
        sessions_rows = await db_module.get_all_sessions(db, limit, offset)
        
        # Get total count of sessions
        cursor = await db.execute("SELECT COUNT(*) FROM sessions")
        total = (await cursor.fetchone())[0]
        
        sessions_list = []
        for r in sessions_rows:
            sessions_list.append(SessionListItem(
                id=r["id"],
                query=r["query"],
                status=r["status"],
                overall_confidence=r.get("overall_confidence"),
                total_claims=r.get("total_claims") or 0,
                verified_claims=r.get("verified_claims") or 0,
                disputed_claims=r.get("disputed_claims") or 0,
                created_at=r.get("created_at"),
                processing_time=r.get("processing_time")
            ))
            
        return SessionListResponse(
            sessions=sessions_list,
            total=total
        )
    finally:
        await db.close()


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a research session and all cascade associated data."""
    db = await db_module.get_db()
    try:
        session = await db_module.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await db_module.delete_session(db, session_id)
        return {"status": "success", "message": f"Session {session_id} and all related claims/sources deleted"}
    finally:
        await db.close()
