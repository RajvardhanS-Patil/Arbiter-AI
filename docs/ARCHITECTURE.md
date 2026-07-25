# 🏛️ Arbiter AI — System Architecture

## Overview

Arbiter AI is an **Autonomous Multi-Agent Research & Fact-Verification System** that uses adversarial AI agents to produce trustworthy, citation-backed research reports. Unlike single-model systems, Arbiter AI employs a **courtroom-style architecture** where claims are researched, challenged, debated, and judged.

---

## Agent Architecture — "The Court of Truth"

Arbiter AI uses **6 specialized agents** organized in a courtroom metaphor:

### 1. 🔍 The Investigator (Research Agent)
- **Role**: Receives a topic/query and conducts deep research
- **Responsibilities**:
  - Break down the topic into sub-questions
  - Search multiple sources (web, APIs, databases)
  - Extract atomic claims from gathered information
  - Tag each claim with source URLs, timestamps, and initial confidence
- **Output**: List of `Claim` objects with source citations

### 2. 🛡️ The Verifier (Cross-Verification Agent)
- **Role**: Takes each claim and cross-references against independent sources
- **Responsibilities**:
  - Search for corroborating evidence from different sources
  - Search for contradicting evidence
  - Calculate source diversity score
  - Assign verification status: `VERIFIED`, `DISPUTED`, `UNVERIFIED`
- **Output**: Enriched claims with verification metadata

### 3. 😈 The Devil's Advocate (Adversarial Agent)
- **Role**: Actively tries to DISPROVE every claim
- **Responsibilities**:
  - Generate counter-arguments for each claim
  - Find logical fallacies or reasoning gaps
  - Identify potential biases in sources
  - Challenge temporal validity (is this still true?)
- **Output**: Challenge reports with counter-evidence

### 4. ⚖️ The Judge (Arbitration Agent)
- **Role**: Evaluates the debate between Verifier and Devil's Advocate
- **Responsibilities**:
  - Weigh evidence from both sides
  - Apply confidence scoring algorithm
  - Detect contradictions using semantic similarity
  - Issue final verdict per claim with confidence score (0-100)
- **Output**: Judged claims with final confidence scores

### 5. 📊 The Synthesizer (Report Compilation Agent)
- **Role**: Compiles all judged claims into a coherent, citation-backed report
- **Responsibilities**:
  - Organize claims into logical sections
  - Generate narrative text connecting claims
  - Embed inline citations
  - Create executive summary with overall confidence
  - Generate Claim DNA fingerprints
- **Output**: Final structured report

### 6. 🎯 The Orchestrator (Pipeline Controller)
- **Role**: Manages the entire pipeline and agent communication
- **Responsibilities**:
  - Route messages between agents
  - Track pipeline state and progress
  - Handle errors and retries
  - Emit real-time events for the Observatory dashboard
  - Manage Multi-Model Consensus voting

---

## Data Flow Pipeline

```
User Query
    │
    ▼
┌──────────────┐
│ Orchestrator  │──────────── Real-time Events ──▶ Observatory Dashboard
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Investigator  │ ◀── Web Search APIs
└──────┬───────┘
       │ Claims[]
       ▼
┌──────────────┐
│   Verifier   │ ◀── Cross-reference Sources
└──────┬───────┘
       │ Verified Claims[]
       ▼
┌──────────────────┐
│ Devil's Advocate  │ ◀── Counter-evidence Search
└──────┬───────────┘
       │ Challenged Claims[]
       ▼
┌──────────────┐
│    Judge     │ ◀── Multi-Model Consensus
└──────┬───────┘
       │ Judged Claims[]
       ▼
┌──────────────┐
│ Synthesizer  │
└──────┬───────┘
       │
       ▼
   Final Report
```

---

## Data Models

### Claim Object
```python
class Claim:
    id: str                    # UUID
    text: str                  # The atomic claim statement
    source_urls: list[str]     # Original sources
    source_titles: list[str]   # Source page titles
    timestamp: datetime        # When claim was extracted
    category: str              # Topic category
    
    # Verification metadata
    verification_status: str   # VERIFIED | DISPUTED | UNVERIFIED
    corroborating_sources: list[Source]
    contradicting_sources: list[Source]
    
    # Adversarial metadata
    counter_arguments: list[str]
    logical_fallacies: list[str]
    bias_flags: list[str]
    
    # Judgment metadata
    confidence_score: float    # 0-100
    judge_reasoning: str
    verdict: str               # ACCEPTED | REJECTED | UNCERTAIN
    
    # Claim DNA
    dna_fingerprint: str       # Unique hash encoding verification history
    genealogy: list[ClaimEvent]  # Full history of claim lifecycle
    
    # Temporal
    temporal_relevance: float  # How current/relevant (0-1)
    decay_rate: float          # How fast confidence decays
    last_verified: datetime
```

### Source Object
```python
class Source:
    url: str
    title: str
    domain: str
    credibility_score: float   # 0-100
    credibility_tier: str      # TIER_1 | TIER_2 | TIER_3 | UNKNOWN
    retrieved_at: datetime
    snippet: str               # Relevant excerpt
```

### AgentMessage Object
```python
class AgentMessage:
    id: str
    from_agent: str
    to_agent: str
    message_type: str          # CLAIM | CHALLENGE | VERDICT | STATUS
    content: dict
    timestamp: datetime
    pipeline_id: str
```

### Report Object
```python
class Report:
    id: str
    query: str
    title: str
    executive_summary: str
    sections: list[ReportSection]
    claims: list[Claim]
    overall_confidence: float
    total_sources: int
    contradiction_count: int
    created_at: datetime
    processing_time: float
    agent_messages: list[AgentMessage]  # Full communication log
```

---

## Multi-Model Consensus Architecture

```
         Claim to Verify
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Gemini │ │  Groq  │ │ Model3 │
│  API   │ │  API   │ │  API   │
└───┬────┘ └───┬────┘ └───┬────┘
    │         │         │
    ▼         ▼         ▼
┌─────────────────────────────┐
│    Consensus Aggregator     │
│  (Majority Vote + Weighted) │
└──────────────┬──────────────┘
               │
               ▼
        Final Judgment
```

- Each model independently evaluates the claim
- Results are aggregated using weighted majority voting
- Model weights can be adjusted based on past accuracy
- If all models disagree, claim is marked `UNCERTAIN`

---

## Real-time Communication (WebSocket)

The Orchestrator emits events over WebSocket for the Observatory dashboard:

```json
{
  "event": "agent_message",
  "data": {
    "from": "investigator",
    "to": "verifier",
    "type": "claims_batch",
    "content": "Extracted 12 claims from 5 sources",
    "timestamp": "2025-01-01T00:00:00Z",
    "pipeline_id": "abc-123"
  }
}
```

Event types:
- `pipeline_started` — New research pipeline initiated
- `agent_started` — Agent began processing
- `agent_progress` — Progress update from agent
- `agent_message` — Inter-agent communication
- `agent_completed` — Agent finished processing
- `claim_created` — New claim extracted
- `claim_verified` — Claim verification completed
- `claim_challenged` — Devil's advocate challenged a claim
- `claim_judged` — Judge issued verdict
- `report_ready` — Final report compiled
- `error` — Error occurred in pipeline

---

## Database Schema (SQLite)

```sql
-- Research sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    overall_confidence REAL,
    total_claims INTEGER DEFAULT 0,
    verified_claims INTEGER DEFAULT 0,
    disputed_claims INTEGER DEFAULT 0
);

-- Claims
CREATE TABLE claims (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    text TEXT NOT NULL,
    category TEXT,
    verification_status TEXT DEFAULT 'unverified',
    confidence_score REAL DEFAULT 0,
    verdict TEXT,
    judge_reasoning TEXT,
    dna_fingerprint TEXT,
    temporal_relevance REAL DEFAULT 1.0,
    decay_rate REAL DEFAULT 0.01,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified TIMESTAMP
);

-- Sources
CREATE TABLE sources (
    id TEXT PRIMARY KEY,
    claim_id TEXT REFERENCES claims(id),
    url TEXT,
    title TEXT,
    domain TEXT,
    credibility_score REAL,
    credibility_tier TEXT,
    snippet TEXT,
    relationship TEXT,  -- 'corroborating' | 'contradicting' | 'original'
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent messages (for Observatory)
CREATE TABLE agent_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    message_type TEXT,
    content TEXT,  -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Claim genealogy events
CREATE TABLE claim_events (
    id TEXT PRIMARY KEY,
    claim_id TEXT REFERENCES claims(id),
    event_type TEXT,  -- 'created' | 'verified' | 'challenged' | 'judged' | 'mutated'
    agent TEXT,
    details TEXT,  -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports
CREATE TABLE reports (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    title TEXT,
    executive_summary TEXT,
    sections TEXT,  -- JSON
    overall_confidence REAL,
    total_sources INTEGER,
    contradiction_count INTEGER,
    processing_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
