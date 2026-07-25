# Arbiter AI ⚖️

Arbiter AI is a real-time, multi-agent fact-checking and investigation platform. It employs a swarm of specialized AI agents to analyze complex claims, debate evidence, and synthesize high-accuracy verdicts. The platform features a live "Debate Arena" where users can watch the AI agents deliberate over facts in real-time using WebSockets.

## 🚀 Features

- **Multi-Agent Architecture**: A custom LLM pipeline featuring specialized roles: Orchestrator, Investigator, Fact Verifier, Devil's Advocate, Judge, and Synthesizer.
- **Live Debate Arena**: Real-time WebSocket streaming of the internal AI deliberation process, visualized as a courtroom debate.
- **Document & Text Analysis**: Upload PDFs, TXTs, or paste claims directly for automated fact-checking.
- **Dynamic Reporting**: Generates detailed markdown, JSON, and PDF reports with contradiction heat maps, source citations, and confidence scoring.
- **Responsive UI**: A modern, glassmorphism-inspired UI built with React and Tailwind CSS, fully optimized for both desktop and mobile.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS (with custom utility classes and animations)
- **Icons**: Lucide React
- **Real-time**: Native WebSockets (`useWebSocket` custom hook)
- **Routing**: React Router DOM

### Backend
- **Framework**: FastAPI (Python)
- **AI/LLM**: Groq API (Llama 3 70B/8B models for blazing-fast inference)
- **Concurrency**: `asyncio` for parallel agent execution
- **Real-time**: FastAPI WebSockets
- **Document Parsing**: PyPDF2
- **CORS & Middleware**: Configured for cross-origin production deployments

## ⚙️ Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/RajvardhanS-Patil/Arbiter-AI.git
cd Arbiter-AI
```

### 2. Backend Setup
```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file and add your Groq API Key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Run the FastAPI server
uvicorn main:app --reload
```
The backend will run at `http://localhost:8000`.

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create a .env file for the frontend (optional for local, required for production)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start the Vite development server
npm run dev
```
The frontend will run at `http://localhost:5173`.

## 🌐 Production Deployment

- **Backend**: Hosted on Render (Web Service). Requires the `GROQ_API_KEY` environment variable.
- **Frontend**: Hosted on Render (Static Site). Requires the `VITE_API_URL` environment variable pointing to the deployed backend URL (e.g., `https://arbiter-backend.onrender.com`).

## 🧠 How the AI Pipeline Works

1. **Investigator**: Extracts core, falsifiable claims from the user's input or uploaded document.
2. **Fact Verifier**: Cross-references the claims against knowledge bounds, searching for supporting evidence.
3. **Devil's Advocate**: Actively searches for contradictions, logical fallacies, or opposing viewpoints.
4. **Judge (The Arbiter)**: Weighs the arguments from the Verifier and Advocate to determine a final verdict (Verified, Disputed, or False) with a confidence score.
5. **Synthesizer**: Compiles the entire deliberation into a cohesive, structured report.

## 📄 License

This project was built for InnovaHack.
