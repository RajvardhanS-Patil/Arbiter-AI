"""
Arbiter AI — Orchestrator Agent
The pipeline controller that manages the entire research process.
Routes data between agents, tracks state, and emits real-time events
for the Observatory dashboard via WebSocket.
"""

import uuid
import time
import traceback
from datetime import datetime
from typing import Callable, Coroutine
from agents.base_agent import BaseAgent
from agents.investigator import investigator_agent
from agents.verifier import verifier_agent
from agents.devils_advocate import devils_advocate_agent
from agents.judge import judge_agent
from agents.synthesizer import synthesizer_agent
import database as db_module


class OrchestratorAgent(BaseAgent):
    """
    🎯 The Orchestrator
    Manages the entire multi-agent research pipeline.
    """
    
    AGENT_NAME = "orchestrator"
    AGENT_EMOJI = "🎯"
    
    def __init__(self):
        super().__init__()
        self._ws_broadcast: Callable | None = None
        self._agent_progress = {}  # Track progress per agent
        
        # Register all child agents
        self.agents = {
            "investigator": investigator_agent,
            "verifier": verifier_agent,
            "devils_advocate": devils_advocate_agent,
            "judge": judge_agent,
            "synthesizer": synthesizer_agent,
        }
    
    def set_ws_broadcast(self, broadcast_fn: Callable[..., Coroutine]):
        """Set the WebSocket broadcast function for real-time events."""
        self._ws_broadcast = broadcast_fn
        
        # Set event callback on all agents to route through orchestrator
        for agent in self.agents.values():
            agent.set_event_callback(self._handle_agent_event)
        
        self.set_event_callback(self._handle_agent_event)
    
    async def _handle_agent_event(self, event: dict):
        """Handle events from child agents — save to DB and broadcast via WebSocket."""
        session_id = event.get("metadata", {}).get("session_id", "")
        
        # Save agent message to database
        try:
            database = await db_module.get_db()
            msg_data = {
                "id": event.get("id", str(uuid.uuid4())),
                "session_id": session_id or self._current_session_id,
                "from_agent": event.get("from_agent", "orchestrator"),
                "to_agent": event.get("to_agent", "orchestrator"),
                "message_type": event.get("message_type", "info"),
                "content": event.get("content", ""),
                "metadata": event.get("metadata", {})
            }
            await db_module.create_agent_message(database, msg_data)
            await database.close()
        except Exception as e:
            print(f"⚠️ Failed to save agent message: {e}")
        
        # Broadcast via WebSocket
        if self._ws_broadcast:
            ws_event = {
                "event": event.get("message_type", "agent_message"),
                "timestamp": event.get("timestamp", datetime.utcnow().isoformat()),
                "data": {
                    "from_agent": event.get("from_agent", ""),
                    "to_agent": event.get("to_agent", ""),
                    "message_type": event.get("message_type", ""),
                    "content": event.get("content", ""),
                    "metadata": event.get("metadata", {})
                }
            }
            try:
                await self._ws_broadcast(self._current_session_id, ws_event)
            except Exception as e:
                print(f"⚠️ WebSocket broadcast failed: {e}")
    
    async def run_pipeline(self, session_id: str, query: str, 
                           depth: str = "standard", max_claims: int = 15,
                           enable_debate: bool = True, 
                           enable_multi_model: bool = True) -> dict:
        """
        Run the full research pipeline.
        
        Pipeline order:
        1. Investigator → Extract claims from sources
        2. Verifier → Cross-verify each claim
        3. Devil's Advocate → Challenge each claim
        4. Judge → Issue verdicts with confidence scores
        5. Synthesizer → Compile final report
        """
        self._current_session_id = session_id
        start_time = time.time()
        
        # Update session status
        database = await db_module.get_db()
        await db_module.update_session(database, session_id, {
            "status": "processing",
            "current_agent": "investigator"
        })
        await database.close()
        
        # Emit pipeline start
        await self.emit_event(
            "pipeline_started",
            f"🎯 Arbiter AI pipeline initiated for: '{query}'",
            metadata={
                "session_id": session_id,
                "query": query,
                "depth": depth,
                "max_claims": max_claims
            }
        )
        
        try:
            # ─── Stage 1: Investigation ──────────────────────────────
            await self.emit_event(
                "agent_message",
                "🔍 Dispatching Investigator agent...",
                to_agent="investigator",
                metadata={"session_id": session_id, "stage": 1}
            )
            
            claims = await investigator_agent.process(session_id, {
                "query": query,
                "depth": depth,
                "max_claims": max_claims
            })
            
            if not claims:
                raise RuntimeError("Investigator found no claims. Try a different query.")
            
            # ─── Stage 2: Verification ───────────────────────────────
            await self.emit_event(
                "agent_message",
                f"🛡️ Dispatching Verifier agent for {len(claims)} claims...",
                to_agent="verifier",
                metadata={"session_id": session_id, "stage": 2, "claims_count": len(claims)}
            )
            
            verified_claims = await verifier_agent.process(session_id, claims)
            
            # ─── Stage 3: Devil's Advocate ───────────────────────────
            await self.emit_event(
                "agent_message",
                f"😈 Dispatching Devil's Advocate agent...",
                to_agent="devils_advocate",
                metadata={"session_id": session_id, "stage": 3}
            )
            
            challenged_claims = await devils_advocate_agent.process(session_id, verified_claims)
            
            # ─── Stage 4: Judgment ───────────────────────────────────
            await self.emit_event(
                "agent_message",
                f"⚖️ Dispatching Judge agent for final verdicts...",
                to_agent="judge",
                metadata={"session_id": session_id, "stage": 4}
            )
            
            judged_claims = await judge_agent.process(session_id, challenged_claims)
            
            # ─── Stage 5: Synthesis ──────────────────────────────────
            await self.emit_event(
                "agent_message",
                f"📊 Dispatching Synthesizer agent to compile report...",
                to_agent="synthesizer",
                metadata={"session_id": session_id, "stage": 5}
            )
            
            report = await synthesizer_agent.process(session_id, judged_claims)
            
            # ─── Pipeline Complete ───────────────────────────────────
            elapsed = time.time() - start_time
            
            await self.emit_event(
                "pipeline_completed",
                f"✅ Pipeline completed in {elapsed:.1f}s — "
                f"Report: '{report.get('title', 'Untitled')}' "
                f"({report.get('overall_confidence', 0):.1f}% confidence)",
                metadata={
                    "session_id": session_id,
                    "processing_time": round(elapsed, 1),
                    "report_id": report.get("id", ""),
                    "overall_confidence": report.get("overall_confidence", 0)
                }
            )
            
            return report
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            print(f"❌ Pipeline error after {elapsed:.1f}s: {error_msg}")
            traceback.print_exc()
            
            # Update session as failed
            database = await db_module.get_db()
            await db_module.update_session(database, session_id, {
                "status": "failed",
                "processing_time": round(elapsed, 1)
            })
            await database.close()
            
            await self.emit_event(
                "error",
                f"❌ Pipeline failed: {error_msg}",
                metadata={"session_id": session_id, "error": error_msg}
            )
            
            raise
    
    def get_agent_statuses(self) -> dict:
        """Get current status of all agents."""
        statuses = {}
        for name, agent in self.agents.items():
            statuses[name] = {
                "status": agent.status,
                "progress": agent.progress,
                "items_processed": agent.items_processed,
                "total_items": agent.total_items
            }
        return statuses


# Singleton instance
orchestrator_agent = OrchestratorAgent()
