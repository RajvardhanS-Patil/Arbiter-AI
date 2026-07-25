from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import httpx
from config import settings
from groq import Groq

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    reply: str
    model: str

async def call_xai(messages: List[dict]) -> str:
    if not settings.XAI_API_KEY:
        raise ValueError("XAI_API_KEY not configured")
        
    headers = {
        "Authorization": f"Bearer {settings.XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.XAI_MODEL,
        "messages": messages,
        "temperature": 0.5
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        data = response.json()
        return data["choices"][0]["message"]["content"]

def call_groq(messages: List[dict]) -> str:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured")
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.5
    )
    return response.choices[0].message.content

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # System prompt for fact-checking
    system_prompt = {
        "role": "system",
        "content": "You are Grok, an objective, highly intelligent AI fact-checker and legal/debate assistant for Arbiter AI. You analyze statements, verify facts, and provide clear, concise, and accurate responses."
    }
    
    messages = [system_prompt] + [msg.model_dump() for msg in request.messages]
    
    try:
        if settings.XAI_API_KEY:
            # Use Grok (xAI) if available
            reply = await call_xai(messages)
            return ChatResponse(reply=reply, model="grok")
        elif settings.GROQ_API_KEY:
            # Fallback to Groq
            reply = call_groq(messages)
            return ChatResponse(reply=reply, model="groq")
        else:
            raise HTTPException(status_code=500, detail="No AI provider configured (missing XAI_API_KEY or GROQ_API_KEY)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
