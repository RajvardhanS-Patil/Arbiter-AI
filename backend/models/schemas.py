"""
Arbiter AI — Pydantic Data Models
All request/response schemas for the API and internal data structures.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── Request Models ──────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    """Request to start a new research pipeline."""
    query: str = Field(..., min_length=3, max_length=500, description="Topic to research")
    depth: str = Field(default="standard", description="Research depth: quick, standard, deep")
    enable_debate: bool = Field(default=True, description="Enable debate arena")
    enable_multi_model: bool = Field(default=True, description="Enable multi-model consensus")
    max_claims: int = Field(default=15, ge=5, le=30, description="Max claims to extract")


# ─── Source Models ───────────────────────────────────────────────────

class SourceResponse(BaseModel):
    """A source citation."""
    id: str
    url: str = ""
    title: str = ""
    domain: str = ""
    credibility_score: float = 50
    credibility_tier: str = "UNKNOWN"
    snippet: str = ""
    relationship: str = "original"
    retrieved_at: Optional[str] = None


# ─── Claim Models ────────────────────────────────────────────────────

class ClaimEventResponse(BaseModel):
    """A claim lifecycle event."""
    id: str
    event_type: str
    agent: str = ""
    details: dict = {}
    timestamp: Optional[str] = None


class ClaimResponse(BaseModel):
    """A claim with full metadata."""
    id: str
    text: str
    category: str = "general"
    verification_status: str = "unverified"
    confidence_score: float = 0
    verdict: Optional[str] = None
    judge_reasoning: Optional[str] = None
    dna_fingerprint: Optional[str] = None
    temporal_relevance: float = 1.0
    counter_arguments: list[str] = []
    logical_fallacies: list[str] = []
    bias_flags: list[str] = []
    sources: list[SourceResponse] = []
    genealogy: list[ClaimEventResponse] = []
    created_at: Optional[str] = None
    last_verified: Optional[str] = None


class ClaimsListResponse(BaseModel):
    """List of claims with summary stats."""
    claims: list[ClaimResponse] = []
    total: int = 0
    verified_count: int = 0
    disputed_count: int = 0
    unverified_count: int = 0


# ─── Agent Message Models ───────────────────────────────────────────

class AgentMessageResponse(BaseModel):
    """An inter-agent communication message."""
    id: str
    from_agent: str
    to_agent: str
    message_type: str = "info"
    content: str = ""
    metadata: dict = {}
    timestamp: Optional[str] = None


# ─── Debate Models ───────────────────────────────────────────────────

class DebateArgument(BaseModel):
    """One side's argument in a debate round."""
    position: str = ""
    evidence: list[str] = []
    confidence: float = 50


class DebateRound(BaseModel):
    """A single round of debate."""
    round_number: int
    verifier_argument: DebateArgument = DebateArgument()
    devils_advocate_argument: DebateArgument = DebateArgument()


class DebateVerdict(BaseModel):
    """The judge's verdict on a debate."""
    decision: str = "uncertain"
    confidence: float = 50
    reasoning: str = ""


class DebateResponse(BaseModel):
    """A complete debate for a claim."""
    id: str
    claim_id: str
    claim_text: str = ""
    rounds: list[DebateRound] = []
    verdict: DebateVerdict = DebateVerdict()
    created_at: Optional[str] = None


# ─── Consensus Models ───────────────────────────────────────────────

class ConsensusVoteResponse(BaseModel):
    """A single model's vote in multi-model consensus."""
    id: str
    provider: str
    model: str
    verdict: str = ""
    confidence: float = 0
    reasoning: str = ""


# ─── Report Models ───────────────────────────────────────────────────

class ReportSection(BaseModel):
    """A section of the final report."""
    title: str = ""
    content: str = ""
    claim_ids: list[str] = []
    section_confidence: float = 0


class ReportResponse(BaseModel):
    """The final compiled report."""
    id: str
    session_id: str
    title: str = ""
    executive_summary: str = ""
    overall_confidence: float = 0
    sections: list[ReportSection] = []
    total_sources: int = 0
    contradiction_count: int = 0
    processing_time: float = 0
    created_at: Optional[str] = None


# ─── Session Models ──────────────────────────────────────────────────

class SessionProgress(BaseModel):
    """Progress state of each agent."""
    investigator: str = "pending"
    verifier: str = "pending"
    devils_advocate: str = "pending"
    judge: str = "pending"
    synthesizer: str = "pending"


class SessionStatusResponse(BaseModel):
    """Current status of a research session."""
    session_id: str
    query: str
    status: str = "pending"
    current_agent: Optional[str] = None
    progress: SessionProgress = SessionProgress()
    claims_found: int = 0
    claims_verified: int = 0
    elapsed_time: float = 0
    overall_confidence: Optional[float] = None


class SessionListItem(BaseModel):
    """Summary of a session for listing."""
    id: str
    query: str
    status: str = "pending"
    overall_confidence: Optional[float] = None
    total_claims: int = 0
    verified_claims: int = 0
    disputed_claims: int = 0
    created_at: Optional[str] = None
    processing_time: Optional[float] = None


class SessionListResponse(BaseModel):
    """List of sessions."""
    sessions: list[SessionListItem] = []
    total: int = 0


# ─── Contradiction Models ───────────────────────────────────────────

class ContradictionPair(BaseModel):
    """A pair of contradicting claims."""
    claim_a_id: str
    claim_a_text: str
    claim_b_id: str
    claim_b_text: str
    conflict_score: float = 0
    conflict_type: str = "potential_contradiction"
    sources_a: list[str] = []
    sources_b: list[str] = []


class TopicConflict(BaseModel):
    """Conflict density in a topic area."""
    topic: str
    conflict_density: float = 0
    claim_count: int = 0


class ContradictionsResponse(BaseModel):
    """All contradiction data for heat map."""
    session_id: str
    contradiction_matrix: list[ContradictionPair] = []
    topic_conflicts: list[TopicConflict] = []
    total_contradictions: int = 0
    average_conflict_score: float = 0


# ─── Research Start Response ─────────────────────────────────────────

class ResearchStartResponse(BaseModel):
    """Response when a research pipeline is started."""
    session_id: str
    status: str = "started"
    message: str = "Research pipeline initiated"
    websocket_url: str = ""


# ─── Export Response ─────────────────────────────────────────────────

class ExportResponse(BaseModel):
    """Exported report content."""
    format: str
    content: str
    filename: str
