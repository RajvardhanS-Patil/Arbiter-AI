"""
Arbiter AI — Database Module
SQLite async database setup with all table definitions and CRUD helpers.
"""

import aiosqlite
import os
from config import settings

DATABASE_PATH = settings.DATABASE_PATH


async def get_db():
    """Get a database connection."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Initialize database with all tables."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        
        # Sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                depth TEXT DEFAULT 'standard',
                status TEXT DEFAULT 'pending',
                current_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                overall_confidence REAL,
                total_claims INTEGER DEFAULT 0,
                verified_claims INTEGER DEFAULT 0,
                disputed_claims INTEGER DEFAULT 0,
                unverified_claims INTEGER DEFAULT 0,
                total_sources INTEGER DEFAULT 0,
                contradiction_count INTEGER DEFAULT 0,
                processing_time REAL
            )
        """)
        
        # Claims table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id TEXT PRIMARY KEY,
                session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                text TEXT NOT NULL,
                category TEXT,
                verification_status TEXT DEFAULT 'unverified',
                confidence_score REAL DEFAULT 0,
                verdict TEXT,
                judge_reasoning TEXT,
                dna_fingerprint TEXT,
                temporal_relevance REAL DEFAULT 1.0,
                decay_rate REAL DEFAULT 0.01,
                counter_arguments TEXT DEFAULT '[]',
                logical_fallacies TEXT DEFAULT '[]',
                bias_flags TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_verified TIMESTAMP
            )
        """)
        
        # Sources table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                claim_id TEXT REFERENCES claims(id) ON DELETE CASCADE,
                session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                url TEXT,
                title TEXT,
                domain TEXT,
                credibility_score REAL DEFAULT 50,
                credibility_tier TEXT DEFAULT 'UNKNOWN',
                snippet TEXT,
                relationship TEXT DEFAULT 'original',
                retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Agent messages table (for Observatory)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agent_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                message_type TEXT,
                content TEXT,
                metadata TEXT DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Claim events table (for Genealogy)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS claim_events (
                id TEXT PRIMARY KEY,
                claim_id TEXT REFERENCES claims(id) ON DELETE CASCADE,
                session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                event_type TEXT NOT NULL,
                agent TEXT,
                details TEXT DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Reports table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                title TEXT,
                executive_summary TEXT,
                sections TEXT DEFAULT '[]',
                overall_confidence REAL,
                total_sources INTEGER DEFAULT 0,
                contradiction_count INTEGER DEFAULT 0,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Debates table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS debates (
                id TEXT PRIMARY KEY,
                claim_id TEXT REFERENCES claims(id) ON DELETE CASCADE,
                session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                claim_text TEXT,
                rounds TEXT DEFAULT '[]',
                verdict TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Consensus votes table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS consensus_votes (
                id TEXT PRIMARY KEY,
                claim_id TEXT REFERENCES claims(id) ON DELETE CASCADE,
                session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                verdict TEXT,
                confidence REAL,
                reasoning TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_claims_session ON claims(session_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sources_claim ON sources(claim_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sources_session ON sources(session_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON agent_messages(session_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_events_claim ON claim_events(claim_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_debates_session ON debates(session_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_votes_claim ON consensus_votes(claim_id)")
        
        await db.commit()
        print("✅ Database initialized successfully")


# ─── CRUD Helpers ────────────────────────────────────────────────────

async def create_session(db, session_data: dict) -> dict:
    """Create a new research session."""
    await db.execute(
        """INSERT INTO sessions (id, query, depth, status) 
           VALUES (?, ?, ?, ?)""",
        (session_data["id"], session_data["query"], 
         session_data.get("depth", "standard"), "pending")
    )
    await db.commit()
    return session_data


async def update_session(db, session_id: str, updates: dict):
    """Update session fields."""
    set_clauses = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [session_id]
    await db.execute(
        f"UPDATE sessions SET {set_clauses} WHERE id = ?",
        values
    )
    await db.commit()


async def get_session(db, session_id: str) -> dict | None:
    """Get a session by ID."""
    cursor = await db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = await cursor.fetchone()
    if row:
        return dict(row)
    return None


async def get_all_sessions(db, limit: int = 20, offset: int = 0) -> list:
    """Get all sessions with pagination."""
    cursor = await db.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def create_claim(db, claim_data: dict) -> dict:
    """Insert a claim into the database."""
    import json
    await db.execute(
        """INSERT INTO claims (id, session_id, text, category, verification_status, 
           confidence_score, dna_fingerprint, counter_arguments, logical_fallacies, bias_flags)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (claim_data["id"], claim_data["session_id"], claim_data["text"],
         claim_data.get("category", "general"),
         claim_data.get("verification_status", "unverified"),
         claim_data.get("confidence_score", 0),
         claim_data.get("dna_fingerprint", ""),
         json.dumps(claim_data.get("counter_arguments", [])),
         json.dumps(claim_data.get("logical_fallacies", [])),
         json.dumps(claim_data.get("bias_flags", [])))
    )
    await db.commit()
    return claim_data


async def update_claim(db, claim_id: str, updates: dict):
    """Update claim fields."""
    import json
    # Serialize list/dict fields
    for key in ["counter_arguments", "logical_fallacies", "bias_flags"]:
        if key in updates and isinstance(updates[key], (list, dict)):
            updates[key] = json.dumps(updates[key])
    
    set_clauses = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [claim_id]
    await db.execute(
        f"UPDATE claims SET {set_clauses} WHERE id = ?",
        values
    )
    await db.commit()


async def get_claims_by_session(db, session_id: str) -> list:
    """Get all claims for a session."""
    import json
    cursor = await db.execute(
        "SELECT * FROM claims WHERE session_id = ? ORDER BY created_at",
        (session_id,)
    )
    rows = await cursor.fetchall()
    claims = []
    for r in rows:
        claim = dict(r)
        # Parse JSON fields
        for field in ["counter_arguments", "logical_fallacies", "bias_flags"]:
            if claim.get(field):
                try:
                    claim[field] = json.loads(claim[field])
                except (json.JSONDecodeError, TypeError):
                    claim[field] = []
        claims.append(claim)
    return claims


async def create_source(db, source_data: dict) -> dict:
    """Insert a source."""
    await db.execute(
        """INSERT INTO sources (id, claim_id, session_id, url, title, domain, 
           credibility_score, credibility_tier, snippet, relationship)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (source_data["id"], source_data.get("claim_id"), source_data.get("session_id"),
         source_data.get("url", ""), source_data.get("title", ""),
         source_data.get("domain", ""), source_data.get("credibility_score", 50),
         source_data.get("credibility_tier", "UNKNOWN"),
         source_data.get("snippet", ""), source_data.get("relationship", "original"))
    )
    await db.commit()
    return source_data


async def get_sources_by_claim(db, claim_id: str) -> list:
    """Get all sources for a claim."""
    cursor = await db.execute(
        "SELECT * FROM sources WHERE claim_id = ? ORDER BY credibility_score DESC",
        (claim_id,)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_sources_by_session(db, session_id: str) -> list:
    """Get all sources for a session."""
    cursor = await db.execute(
        "SELECT * FROM sources WHERE session_id = ? ORDER BY credibility_score DESC",
        (session_id,)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def create_agent_message(db, msg_data: dict) -> dict:
    """Insert an agent message."""
    import json
    await db.execute(
        """INSERT INTO agent_messages (id, session_id, from_agent, to_agent, 
           message_type, content, metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (msg_data["id"], msg_data["session_id"], msg_data["from_agent"],
         msg_data["to_agent"], msg_data.get("message_type", "info"),
         msg_data.get("content", ""), json.dumps(msg_data.get("metadata", {})))
    )
    await db.commit()
    return msg_data


async def get_messages_by_session(db, session_id: str) -> list:
    """Get all agent messages for a session."""
    import json
    cursor = await db.execute(
        "SELECT * FROM agent_messages WHERE session_id = ? ORDER BY timestamp",
        (session_id,)
    )
    rows = await cursor.fetchall()
    messages = []
    for r in rows:
        msg = dict(r)
        if msg.get("metadata"):
            try:
                msg["metadata"] = json.loads(msg["metadata"])
            except (json.JSONDecodeError, TypeError):
                msg["metadata"] = {}
        messages.append(msg)
    return messages


async def create_claim_event(db, event_data: dict) -> dict:
    """Insert a claim lifecycle event."""
    import json
    await db.execute(
        """INSERT INTO claim_events (id, claim_id, session_id, event_type, agent, details)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (event_data["id"], event_data["claim_id"], event_data.get("session_id"),
         event_data["event_type"], event_data.get("agent", ""),
         json.dumps(event_data.get("details", {})))
    )
    await db.commit()
    return event_data


async def get_claim_events(db, claim_id: str) -> list:
    """Get all events for a claim (genealogy)."""
    import json
    cursor = await db.execute(
        "SELECT * FROM claim_events WHERE claim_id = ? ORDER BY timestamp",
        (claim_id,)
    )
    rows = await cursor.fetchall()
    events = []
    for r in rows:
        event = dict(r)
        if event.get("details"):
            try:
                event["details"] = json.loads(event["details"])
            except (json.JSONDecodeError, TypeError):
                event["details"] = {}
        events.append(event)
    return events


async def create_report(db, report_data: dict) -> dict:
    """Insert a report."""
    import json
    await db.execute(
        """INSERT INTO reports (id, session_id, title, executive_summary, sections,
           overall_confidence, total_sources, contradiction_count, processing_time)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (report_data["id"], report_data["session_id"], report_data.get("title", ""),
         report_data.get("executive_summary", ""),
         json.dumps(report_data.get("sections", [])),
         report_data.get("overall_confidence", 0),
         report_data.get("total_sources", 0),
         report_data.get("contradiction_count", 0),
         report_data.get("processing_time", 0))
    )
    await db.commit()
    return report_data


async def get_report_by_session(db, session_id: str) -> dict | None:
    """Get the report for a session."""
    import json
    cursor = await db.execute(
        "SELECT * FROM reports WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
        (session_id,)
    )
    row = await cursor.fetchone()
    if row:
        report = dict(row)
        if report.get("sections"):
            try:
                report["sections"] = json.loads(report["sections"])
            except (json.JSONDecodeError, TypeError):
                report["sections"] = []
        return report
    return None


async def create_debate(db, debate_data: dict) -> dict:
    """Insert a debate record."""
    import json
    await db.execute(
        """INSERT INTO debates (id, claim_id, session_id, claim_text, rounds, verdict)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (debate_data["id"], debate_data["claim_id"], debate_data["session_id"],
         debate_data.get("claim_text", ""),
         json.dumps(debate_data.get("rounds", [])),
         json.dumps(debate_data.get("verdict", {})))
    )
    await db.commit()
    return debate_data


async def get_debates_by_session(db, session_id: str) -> list:
    """Get all debates for a session."""
    import json
    cursor = await db.execute(
        "SELECT * FROM debates WHERE session_id = ? ORDER BY created_at",
        (session_id,)
    )
    rows = await cursor.fetchall()
    debates = []
    for r in rows:
        debate = dict(r)
        for field in ["rounds", "verdict"]:
            if debate.get(field):
                try:
                    debate[field] = json.loads(debate[field])
                except (json.JSONDecodeError, TypeError):
                    debate[field] = [] if field == "rounds" else {}
        debates.append(debate)
    return debates


async def create_consensus_vote(db, vote_data: dict) -> dict:
    """Insert a consensus vote."""
    await db.execute(
        """INSERT INTO consensus_votes (id, claim_id, session_id, provider, model,
           verdict, confidence, reasoning)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (vote_data["id"], vote_data["claim_id"], vote_data["session_id"],
         vote_data["provider"], vote_data["model"],
         vote_data.get("verdict", ""), vote_data.get("confidence", 0),
         vote_data.get("reasoning", ""))
    )
    await db.commit()
    return vote_data


async def get_consensus_votes(db, claim_id: str) -> list:
    """Get all consensus votes for a claim."""
    cursor = await db.execute(
        "SELECT * FROM consensus_votes WHERE claim_id = ? ORDER BY created_at",
        (claim_id,)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def delete_session(db, session_id: str):
    """Delete a session and all associated data (cascade)."""
    await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    await db.commit()
