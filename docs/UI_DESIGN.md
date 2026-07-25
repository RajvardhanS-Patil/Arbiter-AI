# 🎨 Arbiter AI — UI/UX Design Specification

## Design Philosophy

**"Dark Authority"** — A dark, premium interface that conveys trust, intelligence, and power. Think mission-control meets legal chamber.

---

## Color System

### Primary Palette
```css
--color-bg-primary: #0a0a0f;         /* Deep space black */
--color-bg-secondary: #12121a;       /* Elevated surface */
--color-bg-tertiary: #1a1a2e;        /* Cards, panels */
--color-bg-glass: rgba(26, 26, 46, 0.7); /* Glassmorphism */

--color-accent-primary: #7c3aed;     /* Royal purple — main accent */
--color-accent-secondary: #06b6d4;   /* Cyan — secondary accent */
--color-accent-gold: #f59e0b;        /* Gold — for premium elements */

--color-text-primary: #f1f5f9;       /* Bright white text */
--color-text-secondary: #94a3b8;     /* Muted text */
--color-text-tertiary: #64748b;      /* Subtle text */
```

### Semantic Colors
```css
--color-verified: #10b981;           /* Emerald green */
--color-disputed: #ef4444;           /* Red */
--color-uncertain: #f59e0b;          /* Amber */
--color-unverified: #6b7280;         /* Gray */

--color-confidence-high: #10b981;    /* 80-100 */
--color-confidence-medium: #f59e0b;  /* 50-79 */
--color-confidence-low: #ef4444;     /* 0-49 */
```

### Agent Colors (for Observatory & Avatars)
```css
--color-agent-orchestrator: #8b5cf6; /* Purple */
--color-agent-investigator: #3b82f6; /* Blue */
--color-agent-verifier: #10b981;     /* Green */
--color-agent-devils-advocate: #ef4444; /* Red */
--color-agent-judge: #f59e0b;        /* Gold */
--color-agent-synthesizer: #06b6d4;  /* Cyan */
```

---

## Typography

### Font Stack
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
--font-display: 'Outfit', sans-serif;  /* For headings */
```

### Scale
```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
--text-5xl: 3rem;      /* 48px */
```

---

## Spacing & Layout

```css
--space-1: 0.25rem;
--space-2: 0.5rem;
--space-3: 0.75rem;
--space-4: 1rem;
--space-6: 1.5rem;
--space-8: 2rem;
--space-12: 3rem;
--space-16: 4rem;

--radius-sm: 0.375rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-xl: 1rem;
--radius-2xl: 1.5rem;
--radius-full: 9999px;
```

---

## Effects

### Glassmorphism
```css
.glass {
  background: var(--color-bg-glass);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

### Glow Effects
```css
.glow-purple {
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.3),
              0 0 40px rgba(124, 58, 237, 0.1);
}

.glow-cyan {
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.3),
              0 0 40px rgba(6, 182, 212, 0.1);
}
```

### Animations
```css
/* Pulse for active agents */
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 10px rgba(124, 58, 237, 0.3); }
  50% { box-shadow: 0 0 30px rgba(124, 58, 237, 0.6); }
}

/* Flowing particles between agents */
@keyframes flow-particle {
  0% { transform: translateX(0); opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { transform: translateX(100%); opacity: 0; }
}

/* Typing indicator for agents "thinking" */
@keyframes thinking-dots {
  0%, 20% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}

/* Gavel strike for verdict */
@keyframes gavel-strike {
  0% { transform: rotate(-30deg); }
  50% { transform: rotate(0deg); }
  60% { transform: scale(1.2); }
  100% { transform: scale(1) rotate(0deg); }
}
```

---

## Page Layouts

### 1. Home Page — Research Input
```
┌────────────────────────────────────────────────────┐
│  🏛️ ARBITER AI                     [History] [About]│
├────────────────────────────────────────────────────┤
│                                                     │
│              ⚖️ (Animated Logo)                     │
│                                                     │
│         "The Court of Truth Awaits"                 │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  🔍  Enter a topic to investigate...          │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│   [Quick] [Standard] [Deep]     [⚡ Investigate]   │
│                                                     │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐             │
│   │ Recent  │ │ Recent  │ │ Recent  │              │
│   │Session 1│ │Session 2│ │Session 3│              │
│   └─────────┘ └─────────┘ └─────────┘             │
│                                                     │
│   Stats: 150 claims verified | 45 sessions | 92% avg│
└────────────────────────────────────────────────────┘
```

### 2. Research/Observatory Page — Live Pipeline
```
┌────────────────────────────────────────────────────┐
│  🏛️ ARBITER AI    "Climate Change..."   [Cancel]   │
├────────────────────────────────────────────────────┤
│  Pipeline Progress                                  │
│  [🔍 Investigating] → [🛡️ Verifying] → [😈 ...] → │
│  ──────────███████░░░░░░░░░░────── 35%             │
├──────────────────────────┬─────────────────────────┤
│  Agent Cards (2x3 grid)  │  Live Message Stream    │
│  ┌──────┐ ┌──────┐      │  ┌────────────────────┐│
│  │Invest│ │Verif │      │  │🔍→🛡️ Found 12     ││
│  │✅Done│ │⚙️Work│      │  │   claims from 5    ││
│  │12/12 │ │ 5/12 │      │  │   sources          ││
│  └──────┘ └──────┘      │  │                    ││
│  ┌──────┐ ┌──────┐      │  │😈→⚖️ Challenging  ││
│  │Devil │ │Judge │      │  │   claim about      ││
│  │⏳Wait│ │⏳Wait│      │  │   temperature...   ││
│  └──────┘ └──────┘      │  └────────────────────┘│
│  ┌──────┐               │                         │
│  │Synth │               │  Stats                  │
│  │⏳Wait│               │  Claims: 12 | Verified: 5│
│  └──────┘               │  Sources: 24 | Time: 45s │
└──────────────────────────┴─────────────────────────┘
```

### 3. Report Page — Interactive Report
```
┌────────────────────────────────────────────────────┐
│  🏛️ ARBITER AI    Report: Climate Change   [Export] │
├────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────┐│
│  │  EXECUTIVE SUMMARY                              ││
│  │  Overall Confidence: [===== 78.5% =====]       ││
│  │  12 claims analyzed | 8 verified | 3 disputed  ││
│  │  24 sources consulted | 3 contradictions found ││
│  └────────────────────────────────────────────────┘│
│                                                     │
│  [📋 Claims] [🔥 Contradictions] [🧬 DNA Graph]    │
│  [📡 Sources] [⚔️ Debates]                         │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ ✅ Claim 1: "Global temps rose 1.1°C..."    │   │
│  │    Confidence: 92.5  |  Sources: 5           │   │
│  │    [▼ Expand for details]                    │   │
│  ├─────────────────────────────────────────────┤   │
│  │ ⚠️ Claim 2: "Arctic ice will melt by..."    │   │
│  │    Confidence: 45.2  |  Sources: 3           │   │
│  │    [▼ Expand for details]                    │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

### 4. Claim Detail — Drill-Down View
```
┌────────────────────────────────────────────────────┐
│  ← Back to Report                                   │
├────────────────────────────────────────────────────┤
│                                                     │
│  "Global temperatures have risen 1.1°C..."          │
│  ┌──────────┐                                       │
│  │ 92.5     │  ✅ ACCEPTED                         │
│  │ Confidence│  Verified by 5 sources               │
│  └──────────┘                                       │
│                                                     │
│  ┌─── SOURCES ────┐  ┌─── DEBATE ──────────────┐  │
│  │ 🥇 IPCC (95)  │  │ 🛡️ Verifier:            │  │
│  │ 🥇 NASA (93)  │  │ "Strongly supported..."  │  │
│  │ 🥈 BBC  (82)  │  │                          │  │
│  │ 🥈 Wiki (75)  │  │ 😈 Devil's Advocate:     │  │
│  │ 🥉 Blog (45)  │  │ "Methodology questions.."│  │
│  └────────────────┘  │                          │  │
│                       │ ⚖️ Judge: "Evidence      │  │
│  ┌─── GENEALOGY ──┐  │ overwhelmingly supports" │  │
│  │ BORN → SOURCED │  └──────────────────────────┘  │
│  │ → VERIFIED →   │                                │
│  │ CHALLENGED →   │                                │
│  │ JUDGED ✅      │                                │
│  └────────────────┘                                │
└────────────────────────────────────────────────────┘
```

---

## Component Design Specs

### Confidence Gauge
- Circular gauge component (SVG-based)
- Color transitions: green (80+) → amber (50-79) → red (0-49)
- Animated fill on mount
- Number centered with gradient text

### Agent Avatar Cards
- Emoji-based avatars with gradient background matching agent color
- Pulsing glow when active
- Status indicator dot (green=done, amber=working, gray=waiting)
- Mini progress bar

### Claim Cards
- Glass-morphism background
- Left border colored by verdict (green/red/amber)
- Expandable accordion for details
- Hover: subtle lift + glow effect

### Message Stream
- Scrolling feed with auto-scroll to bottom
- Each message has agent avatar, colored by sender
- Arrow showing direction (from → to)
- Timestamp in subtle text
- New messages animate in with slide-up

### Heat Map
- CSS Grid-based heat map
- Cell colors: blue → yellow → red gradient
- Animated pulsing on high-conflict cells
- Hover tooltip with claim details

### Pipeline Flow
- Horizontal flow with agent icons
- Animated dashed line connections
- Glowing particle animation on active connection
- Progress indicator under each agent

---

## Responsive Design

### Breakpoints
```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
```

### Mobile Adaptations
- Stack observatory grid vertically
- Full-width claim cards
- Bottom navigation instead of sidebar
- Simplified heat map (list view)
- Collapsible agent cards

---

## Micro-Animations

1. **Page Load**: Fade-in + slide-up for content sections
2. **Search Submit**: Ripple effect on button, input border glow
3. **Agent Activation**: Card scales up slightly + glow pulse
4. **New Claim**: Slides in from left with fade
5. **Verdict Render**: Stamp animation with slight rotation
6. **Confidence Change**: Counter animation (numbers counting up/down)
7. **Tab Switch**: Smooth crossfade between tab content
8. **Card Expand**: Smooth height transition with content fade-in
9. **Pipeline Progress**: Smooth width transition on progress bar
10. **Heat Map Cell**: Gentle pulse on hover, color intensity shift
