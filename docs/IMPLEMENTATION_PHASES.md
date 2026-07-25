# 🚀 Arbiter AI — Implementation Phases

## Time Budget: 24 Hours

### Phase Allocation
| Phase | Duration | Focus |
|-------|:--------:|-------|
| Phase 1: Foundation | 3 hrs | Backend setup, DB, LLM service, search |
| Phase 2: Agents | 5 hrs | All 6 agents with full logic |
| Phase 3: API & WebSocket | 2 hrs | REST endpoints + WebSocket events |
| Phase 4: Frontend Foundation | 3 hrs | React setup, design system, layout |
| Phase 5: Core UI Pages | 4 hrs | Home, Observatory, Report pages |
| Phase 6: Unique Features UI | 4 hrs | Debate Arena, DNA Graph, Heat Map |
| Phase 7: Polish & Demo | 3 hrs | Animations, bugs, demo prep |

---

## Phase 1: Foundation (Hours 0-3)

### 1.1 Backend Setup
- [ ] Initialize Python project with FastAPI
- [ ] Create `requirements.txt` with all dependencies
- [ ] Set up project structure (models/, agents/, services/, routes/)
- [ ] Create `config.py` with environment variable loading
- [ ] Create `.env.example` with all required variables

### 1.2 Database
- [ ] Create `database.py` with SQLite async setup
- [ ] Define all tables (sessions, claims, sources, agent_messages, claim_events, reports)
- [ ] Create initialization function
- [ ] Create helper functions for CRUD operations

### 1.3 Data Models
- [ ] Create Pydantic models for Claim, Source, Session, Report
- [ ] Create request/response models for API
- [ ] Create AgentMessage model for Observatory

### 1.4 Services
- [ ] Create `llm_service.py` — abstraction over Gemini + Groq
  - Provider factory pattern
  - Retry logic with exponential backoff
  - Rate limit handling
- [ ] Create `search_service.py` — DuckDuckGo + Wikipedia search
  - Search with retry
  - Result parsing and deduplication
- [ ] Create `credibility_service.py` — Source credibility scoring
  - Domain tier database
  - Content signal analysis
- [ ] Create `claim_dna_service.py` — DNA fingerprinting
  - Hash generation
  - Event tracking

### Deliverable: Backend can connect to LLMs, search web, score sources

---

## Phase 2: Agents (Hours 3-8)

### 2.1 Base Agent
- [ ] Create `base_agent.py` with:
  - Async processing interface
  - Event emission (for Observatory)
  - Error handling
  - Progress tracking

### 2.2 Investigator Agent
- [ ] Receive query, break into sub-questions
- [ ] Search multiple sources per sub-question
- [ ] Extract atomic claims using LLM
- [ ] Attach source citations to each claim
- [ ] Emit events: claim_created, agent_progress

### 2.3 Verifier Agent
- [ ] Take each claim, search for independent corroboration
- [ ] Find contradicting evidence
- [ ] Calculate source diversity
- [ ] Assign verification status
- [ ] Emit events: claim_verified

### 2.4 Devil's Advocate Agent
- [ ] Generate counter-arguments for each claim
- [ ] Search for disproving evidence
- [ ] Identify logical fallacies
- [ ] Flag potential biases
- [ ] Emit events: claim_challenged

### 2.5 Judge Agent
- [ ] Evaluate Verifier vs Devil's Advocate arguments
- [ ] Apply Multi-Model Consensus (send to Gemini + Groq)
- [ ] Calculate final confidence score
- [ ] Issue verdict with reasoning
- [ ] Apply temporal decay adjustments
- [ ] Emit events: claim_judged

### 2.6 Synthesizer Agent
- [ ] Organize claims into logical sections
- [ ] Generate report narrative using LLM
- [ ] Embed inline citations
- [ ] Calculate overall confidence
- [ ] Generate executive summary
- [ ] Emit events: report_ready

### 2.7 Orchestrator
- [ ] Pipeline state management
- [ ] Sequential agent execution with event routing
- [ ] WebSocket event broadcasting
- [ ] Error handling and recovery
- [ ] Progress tracking

### Deliverable: Full pipeline runs end-to-end, produces report from query

---

## Phase 3: API & WebSocket (Hours 8-10)

### 3.1 REST Endpoints
- [ ] `POST /api/v1/research` — Start pipeline
- [ ] `GET /api/v1/research/{id}` — Get status
- [ ] `GET /api/v1/research/{id}/claims` — Get claims
- [ ] `GET /api/v1/reports/{id}` — Get report
- [ ] `GET /api/v1/reports/{id}/export` — Export report
- [ ] `GET /api/v1/research/{id}/debate` — Get debate data
- [ ] `GET /api/v1/claims/{id}/dna` — Get claim DNA
- [ ] `GET /api/v1/research/{id}/contradictions` — Get contradictions
- [ ] `GET /api/v1/research/{id}/sources` — Get sources
- [ ] `GET /api/v1/sessions` — Get history
- [ ] `DELETE /api/v1/sessions/{id}` — Delete session

### 3.2 WebSocket
- [ ] WebSocket endpoint at `/ws/session/{id}`
- [ ] Connection management (connect/disconnect)
- [ ] Event broadcasting from Orchestrator
- [ ] Event queue for events before client connects

### 3.3 CORS & Middleware
- [ ] CORS configuration for frontend
- [ ] Request logging middleware
- [ ] Error handling middleware

### Deliverable: All API endpoints working, WebSocket streaming events

---

## Phase 4: Frontend Foundation (Hours 10-13)

### 4.1 React + Vite Setup
- [ ] Initialize Vite project with React template
- [ ] Install dependencies (react-router-dom, lucide-react, d3, recharts)
- [ ] Configure Vite proxy for backend API

### 4.2 Design System (index.css)
- [ ] CSS custom properties (colors, typography, spacing)
- [ ] Global resets and base styles
- [ ] Glassmorphism utility classes
- [ ] Animation keyframes
- [ ] Responsive breakpoints

### 4.3 Core Components
- [ ] `Navbar.jsx` — Top navigation with logo and links
- [ ] `SearchInput.jsx` — Animated search input with glow
- [ ] `LoadingSpinner.jsx` — Custom loading animation
- [ ] `ConfidenceBadge.jsx` — Color-coded confidence display
- [ ] `AgentAvatar.jsx` — Agent icon with color and status

### 4.4 Routing & Layout
- [ ] Set up React Router with all pages
- [ ] Create App layout with Navbar
- [ ] API service client (`api.js`)
- [ ] WebSocket hook (`useWebSocket.js`)

### Deliverable: App shell with navigation, design system, core components

---

## Phase 5: Core UI Pages (Hours 13-17)

### 5.1 Home Page
- [ ] Hero section with animated logo
- [ ] Search input with depth selector
- [ ] Recent sessions cards
- [ ] Platform statistics
- [ ] Animated background

### 5.2 Observatory Page (Research in Progress)
- [ ] Pipeline flow visualization (horizontal agent flow)
- [ ] Agent status cards (6 cards in grid)
- [ ] Live message stream (WebSocket-powered)
- [ ] Real-time statistics panel
- [ ] Progress bar
- [ ] Auto-redirect to report when complete

### 5.3 Report Page
- [ ] Executive summary section with confidence gauge
- [ ] Tab navigation (Claims, Contradictions, DNA, Sources, Debates)
- [ ] Claims list with expandable cards
- [ ] Source list with credibility badges
- [ ] Export buttons (JSON, Markdown)

### 5.4 History Page
- [ ] Session cards with key metrics
- [ ] Delete session functionality
- [ ] Click to view past reports

### Deliverable: All pages functional, connecting to backend

---

## Phase 6: Unique Features UI (Hours 17-21)

### 6.1 Debate Arena Tab
- [ ] Split-screen debate layout
- [ ] Argument cards for Verifier and Devil's Advocate
- [ ] Judge verdict display with gavel animation
- [ ] Round navigation

### 6.2 Claim DNA & Genealogy Graph
- [ ] Interactive graph visualization (D3.js or canvas-based)
- [ ] Nodes = claims, edges = relationships
- [ ] Color-coded by confidence
- [ ] Genealogy timeline for selected claim
- [ ] DNA fingerprint display

### 6.3 Contradiction Heat Map
- [ ] Grid-based heat map component
- [ ] Color gradient (blue → red)
- [ ] Animated pulsing for hot zones
- [ ] Hover tooltips with details
- [ ] Click to see conflicting claims

### 6.4 Multi-Model Consensus Display
- [ ] Jury member cards (one per model)
- [ ] Vote visualization
- [ ] Reasoning comparison
- [ ] Agreement/disagreement indicators

### 6.5 Confidence Gauge Component
- [ ] SVG circular gauge
- [ ] Animated fill
- [ ] Color transitions
- [ ] Number counter animation

### Deliverable: All unique features implemented with animations

---

## Phase 7: Polish & Demo (Hours 21-24)

### 7.1 Polish
- [ ] Review all animations and transitions
- [ ] Fix any visual bugs
- [ ] Ensure responsive design works
- [ ] Optimize loading states
- [ ] Add error handling UI

### 7.2 README & Documentation
- [ ] Create comprehensive README.md
- [ ] Add screenshots/GIFs
- [ ] Setup instructions
- [ ] Architecture overview

### 7.3 Demo Preparation
- [ ] Prepare 2-3 demo queries that showcase all features
- [ ] Test full pipeline end-to-end
- [ ] Create `.env` with real API keys
- [ ] Test with real topics
- [ ] Prepare talking points for judges

### 7.4 Git & Deployment
- [ ] Clean up code
- [ ] Final commit
- [ ] Push to GitHub
- [ ] Optional: Deploy to Vercel + Render

### Deliverable: Production-ready demo with documentation

---

## Critical Path Items

These are the items that block everything else and must be completed on time:

1. **LLM Service** (Phase 1) — Everything depends on AI working
2. **Investigator Agent** (Phase 2) — First agent in pipeline
3. **Orchestrator** (Phase 2) — Pipeline can't run without it
4. **WebSocket** (Phase 3) — Observatory depends on it
5. **Observatory Page** (Phase 5) — Most visually impressive for demo
6. **Report Page** (Phase 5) — Judges need to see output

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| API rate limits hit | Implement aggressive caching, reduce claim count |
| Agent takes too long | Add timeout per agent (60s default) |
| WebSocket disconnects | Auto-reconnect logic, event queue replay |
| Feature too complex | Cut Debate Arena to single round, simplify heat map |
| Time running out | Skip Phase 6 features, focus on Phase 5 polish |
