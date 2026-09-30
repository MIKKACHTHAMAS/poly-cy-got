
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agent import process_message
from database import init_db, get_preferences, save_preferences, delete_preferences

app = FastAPI(title="PolyCyGot API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    language: str = "auto"
    explanation_level: str = "simple"
    session_id: Optional[str] = None
    memory_consent: bool = False

class MemoryRequest(BaseModel):
    user_id: str
    preferred_language: str = "en-IN"
    explanation_level: str = "simple"
    memory_consent: bool = False

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return {"message": "PolyCyGot API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Check memory if session exists and consent given
    prefs = None
    if request.session_id:
        prefs = get_preferences(request.session_id)
    
    language = request.language
    level = request.explanation_level
    
    if prefs:
        if language == "auto":
            language = prefs.get("preferred_language", language)
        if level == "simple" or level is None:
            level = prefs.get("explanation_level", level)
    
    result = await process_message(
        message=request.message,
        language=language,
        explanation_level=level,
        session_id=request.session_id
    )
    
    # Save preferences if consent given
    if request.session_id and request.memory_consent:
        save_preferences(
            request.session_id,
            result["detected_language"],
            level,
            True
        )
    
    return result

@app.get("/memory/{user_id}")
def get_memory(user_id: str):
    prefs = get_preferences(user_id)
    return {"preferences": prefs}

@app.post("/memory")
def save_memory(request: MemoryRequest):
    save_preferences(
        request.user_id,
        request.preferred_language,
        request.explanation_level,
        request.memory_consent
    )
    return {"status": "saved"}

@app.delete("/memory/{user_id}")
def delete_memory(user_id: str):
    delete_preferences(user_id)
    return {"status": "deleted"}
