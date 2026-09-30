
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_BASE = "https://api.sarvam.ai"

async def detect_language(text: str) -> str:
    """Detect language code (en-IN or ta-IN) using Sarvam API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{SARVAM_BASE}/text-lid",
            json={"input": text},
            headers={"api-subscription-key": SARVAM_API_KEY}
        )
        if resp.status_code != 200:
            return "en-IN"  # fallback
        return resp.json().get("language_code", "en-IN")

async def translate_text(text: str, source: str, target: str) -> str:
    """Translate between English and Tamil."""
    if source == target:
        return text
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{SARVAM_BASE}/translate",
            json={
                "input": text,
                "source_language_code": source,
                "target_language_code": target,
                "mode": "formal"
            },
            headers={"api-subscription-key": SARVAM_API_KEY}
        )
        if resp.status_code != 200:
            return text
        return resp.json().get("translated_text", text)
