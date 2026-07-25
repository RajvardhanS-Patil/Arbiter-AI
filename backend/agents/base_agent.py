"""
Arbiter AI — Base Agent
Abstract base class for all agents in the pipeline.
Provides event emission, progress tracking, and error handling.
"""

import uuid
from datetime import datetime
from typing import Any, Callable, Coroutine


class BaseAgent:
    """
    Base class for all Arbiter AI agents.
    Provides common infrastructure for event emission and progress tracking.
    """
    
    AGENT_NAME = "base"
    AGENT_EMOJI = "🤖"
    
    def __init__(self):
        self.progress = 0
        self.status = "idle"  # idle, processing, completed, error
        self.items_processed = 0
        self.total_items = 0
        self._event_callback: Callable | None = None
    
    def set_event_callback(self, callback: Callable[..., Coroutine]):
        """Set the callback for emitting events to the Orchestrator."""
        self._event_callback = callback
    
    async def emit_event(self, event_type: str, content: str, 
                         to_agent: str = "orchestrator", metadata: dict = None):
        """Emit an event to the Observatory via the Orchestrator."""
        event = {
            "id": str(uuid.uuid4()),
            "from_agent": self.AGENT_NAME,
            "to_agent": to_agent,
            "message_type": event_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self._event_callback:
            await self._event_callback(event)
    
    async def emit_progress(self, current: int, total: int, message: str = ""):
        """Emit a progress update."""
        self.items_processed = current
        self.total_items = total
        self.progress = (current / total * 100) if total > 0 else 0
        
        await self.emit_event(
            "agent_progress",
            message or f"Processing {current}/{total}",
            metadata={
                "current": current,
                "total": total,
                "progress": round(self.progress, 1)
            }
        )
    
    async def start(self, session_id: str):
        """Signal that the agent has started processing."""
        self.status = "processing"
        self.progress = 0
        self.items_processed = 0
        
        await self.emit_event(
            "agent_started",
            f"{self.AGENT_EMOJI} {self.AGENT_NAME.title()} agent started",
            metadata={"session_id": session_id}
        )
    
    async def complete(self, session_id: str, summary: str = ""):
        """Signal that the agent has completed processing."""
        self.status = "completed"
        self.progress = 100
        
        await self.emit_event(
            "agent_completed",
            summary or f"{self.AGENT_EMOJI} {self.AGENT_NAME.title()} agent completed",
            metadata={"session_id": session_id}
        )
    
    async def error(self, session_id: str, error_msg: str):
        """Signal that the agent encountered an error."""
        self.status = "error"
        
        await self.emit_event(
            "error",
            f"❌ {self.AGENT_NAME.title()} error: {error_msg}",
            metadata={"session_id": session_id, "error": error_msg}
        )
    
    async def process(self, session_id: str, data: Any) -> Any:
        """
        Main processing method — must be implemented by subclasses.
        
        Args:
            session_id: The research session ID
            data: Input data from the previous agent
            
        Returns:
            Processed data for the next agent
        """
        raise NotImplementedError(f"{self.AGENT_NAME} must implement process()")
