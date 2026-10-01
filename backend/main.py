from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import base64

from agent import process_message
from database import init_db, get_preferences, save_preferences, delete_preferences

app = FastAPI(title="PolyCyGot API")

# CORS — must be before all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://polycygot-frontend.pages.dev",  # Add this
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup():
    init_db()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"message": "PolyCyGot API is running"}


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@app.post("/chat")
async def chat(request: ChatRequest):
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

    if request.session_id and request.memory_consent:
        save_preferences(
            request.session_id,
            result["detected_language"],
            level,
            True
        )

    return result


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Voice input — transcribe audio (Gemini multimodal with fallback)
# ---------------------------------------------------------------------------

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Transcribe speech to text using Gemini with model fallback."""
    audio_bytes = await audio.read()
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gemini_key:
        return {"text": "", "error": "GEMINI_API_KEY not set"}

    try:
        audio_b64 = base64.b64encode(audio_bytes).decode()
        mime = audio.content_type or "audio/wav"

        models = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash"]

        async with httpx.AsyncClient(timeout=60.0) as client:
            for model in models:
                try:
                    resp = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}",
                        json={
                            "contents": [{
                                "parts": [
                                    {"text": (
                                        "Transcribe this audio exactly as spoken. "
                                        "Return ONLY the transcribed text — no commentary, "
                                        "no translation, no formatting. If the audio is in "
                                        "Tamil, return Tamil text. If English, return English."
                                    )},
                                    {"inline_data": {"mime_type": mime, "data": audio_b64}}
                                ]
                            }]
                        }
                    )

                    if resp.status_code == 200:
                        result = resp.json()
                        try:
                            transcript = result["candidates"][0]["content"]["parts"][0]["text"]
                            if transcript:
                                return {"text": transcript.strip()}
                        except (KeyError, IndexError):
                            pass

                    if resp.status_code in (503, 404):
                        print(f"[TRANSCRIBE] {model} unavailable ({resp.status_code}), trying next")
                        continue

                    print(f"[TRANSCRIBE ERROR] {model}: {resp.status_code}")
                    break

                except Exception as e:
                    print(f"[TRANSCRIBE EXCEPTION] {model}: {e}")
                    continue

        return {"text": "", "error": "Transcription temporarily unavailable"}

    except Exception as e:
        print(f"[TRANSCRIBE EXCEPTION] {type(e).__name__}: {e}")
        return {"text": "", "error": str(e)}


# ---------------------------------------------------------------------------
# Voice output — text to speech (Sarvam Bulbul v3)
# ---------------------------------------------------------------------------

@app.post("/speak")
async def speak(text: str, language: str = "ta-IN"):
    """Convert text to speech using Sarvam Bulbul v3."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.sarvam.ai/text-to-speech",
                json={
                    "inputs": [text],
                    "target_language_code": language,
                    "speaker": "priya",
                    "model": "bulbul:v3"
                },
                headers={"api-subscription-key": os.getenv("SARVAM_API_KEY")}
            )
            if resp.status_code != 200:
                print(f"[SPEAK ERROR] {resp.status_code}: {resp.text[:400]}")
                return {"audio": None, "error": resp.text[:200]}
            data = resp.json()
            audios = data.get("audios", [])
            return {"audio": audios[0] if audios else None}
    except Exception as e:
        print(f"[SPEAK EXCEPTION] {type(e).__name__}: {e}")
        return {"audio": None, "error": str(e)}


# ---------------------------------------------------------------------------
# Image analysis — screenshot phishing detection (Gemini with fallback)
# ---------------------------------------------------------------------------

@app.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    """Analyze a screenshot for phishing/scam indicators with model fallback."""
    image_bytes = await image.read()
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gemini_key:
        return {
            "text": (
                "The image analyzer is not configured. "
                "Please contact the administrator."
            )
        }

    try:
        image_b64 = base64.b64encode(image_bytes).decode()
        mime = image.content_type or "image/png"

        prompt = """You are PolyCyGot, a cybersecurity assistant.

Analyze this image carefully. It may be a screenshot of an SMS, email, or message.
If you see a suspicious message, identify the risk indicators and advise the user.
If it's a normal image, say so briefly.
If the image contains personal information (OTP, account number, phone number),
warn the user to redact it before sharing.

Keep the reply under 6 sentences. Speak directly to the user in second person.
Never tell the user to share OTP, passwords, or click unknown links.
Always recommend verifying through official channels."""

        models = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash"]

        async with httpx.AsyncClient(timeout=60.0) as client:
            for model in models:
                try:
                    resp = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}",
                        json={
                            "contents": [{
                                "parts": [
                                    {"text": prompt},
                                    {"inline_data": {"mime_type": mime, "data": image_b64}}
                                ]
                            }]
                        }
                    )

                    if resp.status_code == 200:
                        result = resp.json()
                        try:
                            reply = result["candidates"][0]["content"]["parts"][0]["text"]
                            if reply:
                                return {"text": reply.strip()}
                        except (KeyError, IndexError):
                            pass

                    if resp.status_code in (503, 404):
                        print(f"[IMAGE] {model} unavailable ({resp.status_code}), trying next")
                        continue

                    print(f"[IMAGE ERROR] {model}: {resp.status_code} {resp.text[:200]}")
                    break

                except Exception as e:
                    print(f"[IMAGE EXCEPTION] {model}: {e}")
                    continue

        return {
            "text": (
                "I'm having trouble analyzing images right now — the AI model "
                "is experiencing high demand. Please try again in a moment, "
                "or describe the suspicious message as text instead."
            )
        }

    except Exception as e:
        print(f"[IMAGE EXCEPTION] {type(e).__name__}: {e}")
        return {
            "text": (
                "Something went wrong while processing the image. "
                "Please try again, or describe the message as text."
            )
        }