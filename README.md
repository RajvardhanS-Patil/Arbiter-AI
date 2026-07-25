# ⚖️ Arbiter AI — Autonomous Multi-Agent Research & Fact-Verification System

**Domain:** Gen AI | **Theme:** "The Court of Truth"
Built for the **InnovaHack 24-Hour Hackathon**.

Arbiter AI is a multi-agent pipeline designed to solve one of Generative AI's biggest problems: **hallucinations and unverified claims**. By creating an adversarial courtroom-style environment, agents challenge, defend, and arbitrate claims to produce structured, citation-backed intelligence reports with verified confidence scoring.

---

## 🚀 8 Unique Features That Set Us Apart

1.  **⚔️ Agent Debate Arena**: Sequential validation is replaced by structured debate rounds where the *Verifier* defends claims and the *Devil's Advocate* attacks them with counter-evidence, logical fallacies, and bias flags.
2.  **🧬 Claim DNA & Genealogy**: Every claim receives a unique cryptographic fingerprint reflecting its text, cited sources, and lifecycle history. The lineage shows its transition from extraction (`BORN`) to cross-reference (`VERIFIED`), adversarial challenge (`CHALLENGED`), and verdict (`JUDGED`).
3.  **🔥 Contradiction Heat Map**: An interactive matrix visualization comparing extracted claims. Conflicting claims are flagged dynamically with pulsing colored nodes showing contradiction strengths.
4.  **🤖 Multi-Model Consensus**: Employs a jury system (using **Google Gemini** and **Groq LLaMA 3** concurrently) where models vote on claim verdicts, adjusting scores based on agreement ratios.
5.  **📡 Real-time Agent Observatory**: A mission-control style dashboard displaying inter-agent WebSocket communications, live activity state updates, and pipeline progress graphs.
6.  **⏰ Temporal Decay & Recency**: Claims are date-aware; older claims receive penalties while recent citations receive confidence boosts.
7.  **🕵️ Source Credibility Scoring**: A custom scoring engine evaluating domain authority tiers and content structure quality (hedging terms, numbers, sensationalism).
8.  **📊 Interactive Drill-Down Reports**: A comprehensive fact-checking brief allowing users to expand claim cards to view source snippets, full debates, and DNA lineage.

---

## 🏛️ Multi-Agent Architecture

```
User Query
    │
    ▼
┌──────────────┐
│ Orchestrator  │──────────── Real-time Events (WS) ──▶ Observatory Dashboard
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Investigator  │ ◀── Web Search & Wikipedia (DDG / MediaWiki API)
└──────┬───────┘
       │ [Atomic Claims]
       ▼
┌──────────────┐
│   Verifier   │ ◀── Independent Verification Sources
└──────┬───────┘
       │ [Verified Claims]
       ▼
┌──────────────────┐
│ Devil's Advocate  │ ◀── Adversarial Counter-Evidence
└──────┬───────────┘
       │ [Challenged Claims]
       ▼
┌──────────────┐
│    Judge     │ ◀── Multi-Model Consensus (Gemini + Groq LLaMA)
└──────┬───────┘
       │ [Judged Claims]
       ▼
┌──────────────┐
│ Synthesizer  │ ◀── Report Narrative Compilation
└──────┬───────┘
       │
       ▼
Final Interactive Report
```

---

## 🛠️ Technology Stack (100% Free & Operational)

-   **Backend**: Python, FastAPI, SQLite (async via `aiosqlite`)
-   **AI Providers**: Google Gemini API (`gemini-2.0-flash`), Groq API (`llama-3.3-70b-versatile`)
-   **Search**: DuckDuckGo search library, Wikipedia/MediaWiki API
-   **Frontend**: React (Vite), Tailwind CSS (Vanilla transitions & custom glassmorphism)
-   **Real-time**: FastAPI WebSockets

---

## ⚡ Quick Start & Setup

### 1. Clone & Set Environment Variables
Copy `.env.example` to `.env` in the root folder and add your free API keys:
```env
GEMINI_API_KEY=your_free_gemini_api_key
GROQ_API_KEY=your_free_groq_api_key
```

### 2. Start Backend Server
```bash
# Go to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run ASGI server
uvicorn main:app --reload --port 8000
```
Swagger API docs will be available at `http://localhost:8000/docs`.

### 3. Start Frontend Dashboard
```bash
# Go to frontend
cd frontend

# Install dependencies
npm install

# Start Vite hot reloader
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🎯 Sample Interrogations to Try
-   *Is global temperature increase accelerating faster than 20th century predictions?*
-   *What is the impact of recent appellate court rulings on the classification of crypto utility tokens?*
-   *Did clean energy investments outpace fossil fuel funding in 2024?*
