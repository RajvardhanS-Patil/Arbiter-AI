# 🔌 Arbiter AI — API Design

## Base URL
```
http://localhost:8000/api/v1
```

---

## Endpoints

### 1. Research Pipeline

#### `POST /research`
Start a new research pipeline.

**Request Body:**
```json
{
  "query": "Is climate change accelerating faster than predicted?",
  "depth": "standard",        // "quick" | "standard" | "deep"
  "enable_debate": true,
  "enable_multi_model": true,
  "max_claims": 20
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "status": "started",
  "message": "Research pipeline initiated",
  "websocket_url": "ws://localhost:8000/ws/session/{session_id}"
}
```

#### `GET /research/{session_id}`
Get the current status and results of a research session.

**Response:**
```json
{
  "session_id": "uuid-here",
  "query": "Is climate change accelerating...",
  "status": "processing",     // "pending" | "processing" | "completed" | "failed"
  "current_agent": "verifier",
  "progress": {
    "investigator": "completed",
    "verifier": "processing",
    "devils_advocate": "pending",
    "judge": "pending",
    "synthesizer": "pending"
  },
  "claims_found": 12,
  "claims_verified": 5,
  "elapsed_time": 45.2
}
```

#### `GET /research/{session_id}/claims`
Get all claims for a session with full metadata.

**Query Parameters:**
- `status` — Filter by verification status
- `min_confidence` — Minimum confidence score
- `sort_by` — Sort field (confidence, created_at)

**Response:**
```json
{
  "claims": [
    {
      "id": "claim-uuid",
      "text": "Global temperatures have risen 1.1°C since pre-industrial times",
      "verification_status": "verified",
      "confidence_score": 92.5,
      "verdict": "accepted",
      "sources": [
        {
          "url": "https://...",
          "title": "...",
          "credibility_score": 95,
          "credibility_tier": "TIER_1",
          "relationship": "corroborating"
        }
      ],
      "counter_arguments": ["..."],
      "judge_reasoning": "...",
      "dna_fingerprint": "a3f2c8...",
      "temporal_relevance": 0.95,
      "genealogy": [
        {
          "event": "BORN",
          "agent": "investigator",
          "timestamp": "...",
          "details": "Extracted from IPCC report"
        }
      ]
    }
  ],
  "total": 12,
  "verified_count": 8,
  "disputed_count": 2,
  "unverified_count": 2
}
```

---

### 2. Reports

#### `GET /reports/{session_id}`
Get the final compiled report.

**Response:**
```json
{
  "id": "report-uuid",
  "session_id": "...",
  "title": "Climate Change Acceleration: A Fact-Verified Analysis",
  "executive_summary": "...",
  "overall_confidence": 78.5,
  "sections": [
    {
      "title": "Temperature Trends",
      "content": "...",
      "claims": ["claim-uuid-1", "claim-uuid-2"],
      "section_confidence": 85.2
    }
  ],
  "total_sources": 24,
  "contradiction_count": 3,
  "processing_time": 120.5,
  "created_at": "..."
}
```

#### `GET /reports/{session_id}/export`
Export report in different formats.

**Query Parameters:**
- `format` — "json" | "markdown" | "html"

---

### 3. Debate Arena

#### `GET /research/{session_id}/debate`
Get the debate transcript for a session.

**Response:**
```json
{
  "session_id": "...",
  "debates": [
    {
      "claim_id": "claim-uuid",
      "claim_text": "...",
      "rounds": [
        {
          "round": 1,
          "verifier_argument": {
            "position": "The claim is supported by...",
            "evidence": ["source-1", "source-2"],
            "confidence": 85
          },
          "devils_advocate_argument": {
            "position": "However, recent data suggests...",
            "counter_evidence": ["source-3"],
            "confidence": 40
          }
        }
      ],
      "verdict": {
        "decision": "accepted",
        "confidence": 82,
        "reasoning": "The verifier presented stronger evidence..."
      }
    }
  ]
}
```

---

### 4. Claim DNA & Genealogy

#### `GET /claims/{claim_id}/dna`
Get the full DNA and genealogy of a specific claim.

**Response:**
```json
{
  "claim_id": "...",
  "text": "...",
  "dna_fingerprint": "a3f2c8e9...",
  "genealogy": [
    {
      "event_type": "BORN",
      "agent": "investigator",
      "timestamp": "...",
      "details": {
        "source": "https://...",
        "extraction_method": "direct_quote"
      }
    },
    {
      "event_type": "VERIFIED",
      "agent": "verifier",
      "timestamp": "...",
      "details": {
        "corroborating_sources": 3,
        "confidence_change": "+25"
      }
    }
  ],
  "related_claims": [
    {
      "claim_id": "other-claim-uuid",
      "relationship": "supports",
      "strength": 0.8
    }
  ]
}
```

---

### 5. Contradiction Heat Map

#### `GET /research/{session_id}/contradictions`
Get contradiction data for the heat map.

**Response:**
```json
{
  "session_id": "...",
  "contradiction_matrix": [
    {
      "claim_a_id": "...",
      "claim_a_text": "...",
      "claim_b_id": "...",
      "claim_b_text": "...",
      "conflict_score": 0.85,
      "conflict_type": "direct_contradiction",
      "sources_a": ["..."],
      "sources_b": ["..."]
    }
  ],
  "topic_conflicts": [
    {
      "topic": "Temperature Data",
      "conflict_density": 0.7,
      "claim_count": 5
    }
  ],
  "total_contradictions": 4,
  "average_conflict_score": 0.62
}
```

---

### 6. Source Credibility

#### `GET /research/{session_id}/sources`
Get all sources with credibility scores.

**Response:**
```json
{
  "sources": [
    {
      "id": "source-uuid",
      "url": "https://...",
      "title": "...",
      "domain": "reuters.com",
      "credibility_score": 95,
      "credibility_tier": "TIER_1",
      "signals": {
        "domain_authority": 95,
        "has_author": true,
        "has_date": true,
        "has_citations": true,
        "sensational_language": false
      },
      "claims_supported": 4,
      "claims_contradicted": 0
    }
  ],
  "tier_distribution": {
    "TIER_1": 5,
    "TIER_2": 8,
    "TIER_3": 3,
    "UNKNOWN": 2
  }
}
```

---

### 7. History

#### `GET /sessions`
Get all past research sessions.

**Query Parameters:**
- `limit` — Max results (default: 20)
- `offset` — Pagination offset
- `status` — Filter by status

**Response:**
```json
{
  "sessions": [
    {
      "id": "...",
      "query": "...",
      "status": "completed",
      "overall_confidence": 78.5,
      "total_claims": 15,
      "verified_claims": 12,
      "created_at": "...",
      "processing_time": 120.5
    }
  ],
  "total": 10
}
```

#### `DELETE /sessions/{session_id}`
Delete a research session and all associated data.

---

### 8. WebSocket — Real-time Observatory

#### `WS /ws/session/{session_id}`
Connect to receive real-time pipeline events.

**Event Format:**
```json
{
  "event": "agent_message",
  "timestamp": "2025-01-01T00:00:00Z",
  "data": {
    "from_agent": "investigator",
    "to_agent": "verifier",
    "message_type": "claims_batch",
    "content": "Found 12 claims from 5 sources",
    "metadata": {
      "claims_count": 12,
      "sources_count": 5
    }
  }
}
```

**Event Types:**
| Event | Description |
|-------|-------------|
| `pipeline_started` | Pipeline initialized |
| `agent_started` | Agent began work |
| `agent_progress` | Progress update |
| `agent_message` | Inter-agent communication |
| `agent_completed` | Agent finished |
| `claim_created` | New claim extracted |
| `claim_verified` | Verification complete |
| `claim_challenged` | Devil's advocate challenge |
| `claim_judged` | Final judgment |
| `debate_round` | Debate round update |
| `consensus_vote` | Multi-model vote |
| `report_ready` | Report compiled |
| `pipeline_completed` | Pipeline finished |
| `error` | Error occurred |

---

## Error Handling

All errors follow this format:
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "AI provider rate limit exceeded. Retrying in 5 seconds.",
    "details": {
      "provider": "gemini",
      "retry_after": 5
    }
  }
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|:-----------:|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `SESSION_NOT_FOUND` | 404 | Research session doesn't exist |
| `PIPELINE_FAILED` | 500 | Pipeline encountered unrecoverable error |
| `RATE_LIMITED` | 429 | AI provider rate limited |
| `PROVIDER_ERROR` | 502 | AI provider returned error |
