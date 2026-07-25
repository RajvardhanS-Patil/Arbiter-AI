"""
Arbiter AI — Upload Routes
Handles file uploads (PDF, TXT, DOCX, Images) and triggers the research pipeline based on extracted text.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from models.schemas import ResearchStartResponse
from agents.orchestrator import orchestrator_agent
import database as db_module
import uuid
import asyncio
from services.file_extraction_service import file_extraction_service
from routes.research import active_tasks, run_pipeline_wrapper

router = APIRouter()

@router.post("/upload/verify", response_model=ResearchStartResponse)
async def upload_and_verify(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    query: str = Form(None),
    depth: str = Form("standard"),
    max_claims: int = Form(15),
    enable_debate: bool = Form(True),
    enable_multi_model: bool = Form(True)
):
    """Upload a file, extract its text, and start a research verification session."""
    
    # Read file content
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
        
    # Extract text
    extracted_text = file_extraction_service.extract_text(file.filename, content)
    
    # Use the filename and a snippet of the text as the query topic for tracking
    if query and query.strip():
        query_title = f"{query.strip()[:50]} (w/ {file.filename})"
    else:
        query_title = f"Doc: {file.filename}"
    
    session_id = str(uuid.uuid4())
    
    # Save the session to the DB as pending
    db = await db_module.get_db()
    try:
        await db_module.create_session(db, {
            "id": session_id,
            "query": query_title,
            "depth": depth
        })
    finally:
        await db.close()
    
    # Run pipeline in background using the extracted text as the query context
    if query and query.strip():
        full_context = f"User Query: {query.strip()}\n\nAnalyze the following document content for factual claims in relation to the query:\n\n{extracted_text}"
    else:
        full_context = f"Analyze the following document content for factual claims:\n\n{extracted_text}"
    
    task = asyncio.create_task(
        run_pipeline_wrapper(
            session_id=session_id,
            query=full_context,
            depth=depth,
            max_claims=max_claims,
            enable_debate=enable_debate,
            enable_multi_model=enable_multi_model
        )
    )
    active_tasks[session_id] = task
    
    websocket_url = f"ws://localhost:8000/ws/session/{session_id}"
    
    return ResearchStartResponse(
        session_id=session_id,
        status="started",
        message=f"Extraction successful. Pipeline initiated for {file.filename}",
        websocket_url=websocket_url
    )
