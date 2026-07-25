# 🌟 Arbiter AI — Unique Features Specification

## Feature 1: ⚔️ Agent Debate Arena

### Concept
Instead of sequential verification, agents engage in **adversarial debate rounds**. This mimics a courtroom trial:
- The **Verifier** acts as the prosecution (defending the claim)
- The **Devil's Advocate** acts as the defense (attacking the claim)
- The **Judge** presides and scores each round

### How It Works
1. **Round 1 — Opening Statements**
   - Verifier presents corroborating evidence
   - Devil's Advocate presents counter-evidence
   
2. **Round 2 — Rebuttal**
   - Each agent responds to the other's arguments
   - New evidence can be introduced
   
3. **Round 3 — Closing Arguments**
   - Final summaries from both sides
   - Judge evaluates all arguments

4. **Verdict**
   - Judge assigns confidence score based on debate quality
   - Stronger debates (more evidence) = higher confidence in verdict

### UI Representation
- Split-screen debate view with Verifier on left, Devil's Advocate on right
- Judge at the top center
- Real-time argument streaming
- Score cards updating live
- Animated gavel when verdict is rendered

---

## Feature 2: 🧬 Claim DNA & Genealogy Graph

### Concept
Every claim gets a unique **DNA fingerprint** — a hash that encodes its entire lifecycle. The genealogy shows how claims evolve through the verification pipeline.

### DNA Fingerprint Structure
```
DNA = hash(claim_text + sources + verification_history + confidence_changes)
```

### Genealogy Events
Each claim tracks its full lifecycle:
- `BORN` — Claim first extracted by Investigator
- `SOURCED` — Sources attached
- `VERIFIED` — Cross-verified by Verifier
- `CHALLENGED` — Attacked by Devil's Advocate
- `DEFENDED` — Successfully defended
- `MUTATED` — Claim text refined based on evidence
- `JUDGED` — Final verdict issued
- `ACCEPTED` / `REJECTED` — Final status

### Visualization
- **Interactive graph** using D3.js or vis.js
- Nodes = claims, Edges = relationships (supports, contradicts, derived-from)
- Color-coded by confidence score (green → yellow → red)
- Click any node to see full genealogy timeline
- Animated transitions as claims move through pipeline

---

## Feature 3: 🔥 Contradiction Heat Map

### Concept
A visual heat map showing where contradictions cluster across sources and claims. High-conflict areas pulse with animation.

### How It Works
1. Build a matrix of claims vs. sources
2. Calculate contradiction density per claim-pair
3. Semantic similarity scoring to find conflicting claims
4. Generate heat map with intensity = contradiction strength

### Metrics Tracked
- **Contradiction Density**: How many sources contradict a claim
- **Semantic Conflict Score**: NLP-based similarity between contradicting claims
- **Source Agreement Ratio**: % of sources that agree vs. disagree
- **Topic Conflict Zones**: Which sub-topics have most disagreement

### Visualization
- Grid-based heat map with animated pulsing for hot zones
- Color gradient: Blue (consensus) → Yellow (mild conflict) → Red (strong contradiction)
- Hover to see specific contradicting claims
- Click to drill into the debate between conflicting claims

---

## Feature 4: 🤖 Multi-Model Consensus (Jury System)

### Concept
Use multiple FREE AI models simultaneously. Claims only pass if a **majority of models agree** — like a jury system.

### Models Used (ALL FREE)
1. **Google Gemini** — via free API (generous rate limits)
2. **Groq (LLaMA 3)** — ultra-fast inference, free tier
3. **Fallback: Local heuristic model** — NLP-based fact checker as tiebreaker

### Consensus Algorithm
```
For each claim:
  1. Send to all available models with same prompt
  2. Each model returns: {verdict, confidence, reasoning}
  3. Calculate weighted consensus:
     - Model weight = base_weight × recent_accuracy
     - Consensus = weighted_sum(verdicts) / total_weight
  4. If consensus > 0.7 → VERIFIED
  5. If consensus < 0.3 → DISPUTED
  6. Otherwise → UNCERTAIN
```

### Disagreement Handling
- If models strongly disagree, trigger a **re-evaluation round**
- Each model explains WHY it disagrees
- The Judge agent arbitrates based on reasoning quality
- Persistent disagreements are flagged as `HIGH_UNCERTAINTY`

### UI Display
- Show each model's vote as cards (like jury members)
- Animated voting visualization
- Reasoning comparison panel
- Historical accuracy tracking per model

---

## Feature 5: 📡 Real-time Agent Observatory

### Concept
A live dashboard showing agents communicating in real-time — like a mission control center.

### Components
1. **Pipeline Visualization**
   - Horizontal flow diagram showing all 6 agents
   - Active agent highlighted with glow effect
   - Animated data particles flowing between agents
   - Progress percentage per agent

2. **Message Stream**
   - Live feed of inter-agent communications
   - Color-coded by agent (each has unique color)
   - Message type icons (claim, challenge, verdict)
   - Timestamps and duration tracking

3. **Agent Status Cards**
   - Each agent has a card showing:
     - Current status (idle, processing, complete)
     - Items processed / total
     - Processing time
     - "Thinking" animation when active

4. **Statistics Panel**
   - Claims processed in real-time
   - Verification rate (% verified)
   - Average confidence score
   - Contradictions found
   - Sources consulted

### WebSocket Events
- All pipeline events streamed via WebSocket
- Auto-reconnect on disconnect
- Event replay for review
- Exportable event log

---

## Feature 6: ⏰ Confidence Decay & Time-Awareness

### Concept
Information has a shelf life. Claims lose confidence over time if they can't be re-verified. The system is **temporally aware**.

### Decay Formula
```
current_confidence = original_confidence × e^(-decay_rate × days_since_verification)
```

### Time-Awareness Features
- **Source Date Detection**: Extract and parse dates from sources
- **Recency Boost**: Recent sources (< 30 days) get confidence boost
- **Staleness Penalty**: Sources older than 1 year get penalty
- **Event-Aware**: Detect if a claim references an event with known date
- **Version History**: Track how a claim's confidence changes over time

### UI Display
- Confidence timeline graph per claim
- "Freshness" badge on each claim (Fresh, Current, Aging, Stale)
- Decay curve visualization
- "Last Verified" timestamp prominently displayed

---

## Feature 7: 🕵️ Source Credibility Scoring

### Concept
Not all sources are equal. A credibility engine dynamically ranks sources based on multiple signals.

### Credibility Signals
1. **Domain Authority** (pre-configured tiers)
   - **Tier 1** (90-100): Academic journals, government (.gov), established news (Reuters, AP, BBC)
   - **Tier 2** (70-89): Major publications, Wikipedia, established tech sites
   - **Tier 3** (40-69): Blogs, forums, social media verified accounts
   - **Unknown** (20-39): Unrecognized domains

2. **Content Signals** (dynamically scored)
   - Has author attribution (+5)
   - Has publication date (+5)
   - Contains citations/references (+10)
   - Uses hedging language ("may", "suggests") (+5 for nuance)
   - Contains sensational language (-10)

3. **Cross-Reference Score**
   - How many other credible sources cite this source
   - Agreement ratio with Tier 1 sources

### Credibility Calculation
```
credibility = (domain_tier_score × 0.5) + (content_signals × 0.3) + (cross_ref_score × 0.2)
```

### UI Display
- Source cards with credibility badges (gold, silver, bronze)
- Credibility breakdown tooltip on hover
- Domain tier visualization
- "Trust Chain" — showing which sources cite which

---

## Feature 8: 📊 Interactive Drill-Down Report

### Concept
The final report is not a static document — it's a **rich interactive experience** where users can explore the verification trail of every claim.

### Report Structure
1. **Executive Summary**
   - Overall topic summary
   - Aggregate confidence score (big number with gauge)
   - Key findings highlights
   - Contradiction summary

2. **Claim Cards**
   - Each claim displayed as an expandable card
   - Confidence gauge (0-100)
   - Verdict badge (✅ Accepted, ❌ Rejected, ⚠️ Uncertain)
   - Click to expand and see:
     - Source citations with credibility scores
     - Verification trail (which agents processed it)
     - Debate summary (arguments for/against)
     - Claim DNA genealogy

3. **Source Map**
   - Visual map of all sources used
   - Grouped by domain/type
   - Credibility tiers color-coded
   - Connection lines to claims they support

4. **Contradiction Section**
   - Heat map embedded
   - List of all found contradictions
   - Side-by-side comparison of conflicting claims

5. **Export Options**
   - PDF export
   - Markdown export
   - JSON data export
   - Share link generation

---

## Feature Summary Matrix

| Feature | Uniqueness Level | Complexity | Visual Impact | Demo Value |
|---------|:---:|:---:|:---:|:---:|
| Agent Debate Arena | 🔥🔥🔥 | High | Very High | Excellent |
| Claim DNA & Genealogy | 🔥🔥🔥 | Medium | High | Excellent |
| Contradiction Heat Map | 🔥🔥 | Medium | Very High | Great |
| Multi-Model Consensus | 🔥🔥🔥 | High | Medium | Excellent |
| Agent Observatory | 🔥🔥 | Medium | Very High | Excellent |
| Confidence Decay | 🔥🔥 | Low | Medium | Good |
| Source Credibility | 🔥🔥 | Medium | Medium | Good |
| Interactive Report | 🔥🔥 | Medium | Very High | Excellent |
