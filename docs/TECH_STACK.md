# 🛠️ Arbiter AI — Technology Stack

## Stack Decision: Python (FastAPI) + React (Vite)

This combination gives us the best balance of speed, modern feel, and demo impact for a 24-hour hackathon.

---

## Backend Stack

### Core Framework
- **FastAPI** (Python 3.11+)
  - Async-first, perfect for multi-agent orchestration
  - Built-in WebSocket support for real-time Observatory
  - Auto-generated API docs (Swagger UI)
  - Pydantic models for data validation

### Database
- **SQLite** via **aiosqlite**
  - Zero setup, no external services needed
  - File-based, portable
  - Async support via aiosqlite
  - Perfect for hackathon (no cloud DB needed)

### AI/LLM Providers (ALL FREE)
- **Google Gemini** — `google-genai` package
  - Free tier: 15 RPM, 1M tokens/day
  - Used for: Research, verification, synthesis
  - Model: `gemini-2.0-flash` (fast, free)

- **Groq** — `groq` package
  - Free tier: 30 RPM, 14.4K tokens/min
  - Used for: Multi-model consensus, adversarial checks
  - Model: `llama-3.3-70b-versatile` (powerful, free)

### Web Search (FREE)
- **DuckDuckGo** — `duckduckgo-search` package
  - Completely free, no API key needed
  - Text search, news search
  - Rate-limited but sufficient for hackathon

- **Wikipedia API** — `wikipedia-api` package
  - Free, no API key needed
  - Great for fact-checking baseline

### NLP & Text Processing
- **spaCy** — Entity extraction, NLP pipeline
  - Or lightweight: **rapidfuzz** for string similarity
- **hashlib** — Claim DNA fingerprint generation
- **dateutil** — Date parsing for temporal awareness

### Real-time Communication
- **FastAPI WebSocket** — Built-in
- **asyncio** — Agent orchestration and concurrent processing

### Additional Libraries
- **httpx** — Async HTTP client for API calls
- **beautifulsoup4** — Web scraping for source content extraction
- **python-dotenv** — Environment variable management
- **uvicorn** — ASGI server
- **uuid** — Unique ID generation
- **pydantic** — Data models and validation

---

## Frontend Stack

### Core
- **React 18** via **Vite**
  - Lightning-fast dev server
  - Modern build tooling
  - Hot module replacement

### Styling
- **Vanilla CSS** with CSS Variables
  - Custom design system
  - Dark theme as default
  - Glassmorphism effects
  - CSS animations for micro-interactions

### Visualization Libraries
- **D3.js** — Claim Genealogy Graph, Contradiction Heat Map
  - Or **vis-network** for simpler graph implementation
- **Chart.js** or **Recharts** — Confidence gauges, statistics

### Real-time
- **Native WebSocket API** — Connect to Observatory events
- **React Context** — Global state for WebSocket data

### Icons & Fonts
- **Google Fonts** — Inter or Outfit for modern typography
- **Lucide React** — Beautiful, consistent icon set (free, open source)

### Routing
- **React Router v6** — Client-side routing

---

## Project Structure

```
arbiter-ai/
├── backend/
│   ├── main.py                    # FastAPI app, CORS, WebSocket
│   ├── config.py                  # Environment config, API keys
│   ├── database.py                # SQLite setup, migrations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── claim.py               # Claim data model
│   │   ├── source.py              # Source data model
│   │   ├── report.py              # Report data model
│   │   └── session.py             # Session data model
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent class
│   │   ├── orchestrator.py        # Pipeline controller
│   │   ├── investigator.py        # Research agent
│   │   ├── verifier.py            # Cross-verification agent
│   │   ├── devils_advocate.py     # Adversarial agent
│   │   ├── judge.py               # Arbitration agent
│   │   └── synthesizer.py         # Report compilation agent
│   ├── services/
│   │   ├── __init__.py
│   │   ├── search_service.py      # Web search (DuckDuckGo, Wikipedia)
│   │   ├── llm_service.py         # LLM provider abstraction
│   │   ├── credibility_service.py # Source credibility scoring
│   │   ├── consensus_service.py   # Multi-model consensus
│   │   └── claim_dna_service.py   # Claim DNA fingerprinting
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── research.py            # Research API endpoints
│   │   ├── reports.py             # Report endpoints
│   │   └── websocket.py           # WebSocket endpoint
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── main.jsx               # App entry point
│   │   ├── App.jsx                # Root component, routing
│   │   ├── index.css              # Global styles, design system
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Navbar.jsx
│   │   │   │   ├── Navbar.css
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Sidebar.css
│   │   │   ├── Observatory/
│   │   │   │   ├── Observatory.jsx
│   │   │   │   ├── Observatory.css
│   │   │   │   ├── AgentCard.jsx
│   │   │   │   ├── MessageStream.jsx
│   │   │   │   ├── PipelineFlow.jsx
│   │   │   │   └── StatsPanel.jsx
│   │   │   ├── DebateArena/
│   │   │   │   ├── DebateArena.jsx
│   │   │   │   ├── DebateArena.css
│   │   │   │   ├── ArgumentCard.jsx
│   │   │   │   └── VerdictDisplay.jsx
│   │   │   ├── ClaimDNA/
│   │   │   │   ├── ClaimGraph.jsx
│   │   │   │   ├── ClaimGraph.css
│   │   │   │   ├── GenealogyTimeline.jsx
│   │   │   │   └── DNAFingerprint.jsx
│   │   │   ├── HeatMap/
│   │   │   │   ├── ContradictionHeatMap.jsx
│   │   │   │   └── ContradictionHeatMap.css
│   │   │   ├── Report/
│   │   │   │   ├── ReportView.jsx
│   │   │   │   ├── ReportView.css
│   │   │   │   ├── ClaimCard.jsx
│   │   │   │   ├── ConfidenceGauge.jsx
│   │   │   │   ├── SourceMap.jsx
│   │   │   │   └── ExportPanel.jsx
│   │   │   └── Common/
│   │   │       ├── SearchInput.jsx
│   │   │       ├── LoadingSpinner.jsx
│   │   │       ├── ConfidenceBadge.jsx
│   │   │       └── AgentAvatar.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── HomePage.css
│   │   │   ├── ResearchPage.jsx
│   │   │   ├── ResearchPage.css
│   │   │   ├── ReportPage.jsx
│   │   │   ├── ReportPage.css
│   │   │   └── HistoryPage.jsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   └── useApi.js
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   └── utils/
│   │       ├── constants.js
│   │       └── helpers.js
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FEATURES.md
│   ├── TECH_STACK.md
│   ├── API_DESIGN.md
│   ├── UI_DESIGN.md
│   └── IMPLEMENTATION_PHASES.md
│
├── .env.example
├── .gitignore
├── README.md
└── start.sh / start.bat
```

---

## Environment Variables

```env
# AI Providers
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Server
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Database
DATABASE_URL=sqlite:///./arbiter.db

# Feature Flags
ENABLE_MULTI_MODEL=true
ENABLE_DEBATE_ARENA=true
ENABLE_CLAIM_DNA=true
CONFIDENCE_DECAY_RATE=0.01
```

---

## Free Tier Limits (Important for Hackathon)

| Service | Free Tier | Rate Limit | Notes |
|---------|-----------|------------|-------|
| Gemini API | 15 RPM | 1M tokens/day | More than enough |
| Groq API | 30 RPM | 14.4K tokens/min | Very fast |
| DuckDuckGo | Unlimited | ~20 req/sec | No API key needed |
| Wikipedia API | Unlimited | Reasonable use | No API key needed |
| SQLite | Unlimited | N/A | Local, no limits |

---

## Deployment (Free Options)

### For Demo/Judging
- **Frontend**: Vercel (free) or Netlify (free)
- **Backend**: Render (free) or Railway (free $5 credit)
- **Alternative**: Run both locally for demo

### Quick Start Commands
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```
