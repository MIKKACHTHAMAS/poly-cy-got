import httpx
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_BASE = "https://api.sarvam.ai"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# ---------- Sarvam: language detection ----------

async def detect_language(text: str) -> str:
    """Detect language code (en-IN or ta-IN) using Sarvam API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{SARVAM_BASE}/text-lid",
            json={"input": text},
            headers={"api-subscription-key": SARVAM_API_KEY}
        )
        if resp.status_code != 200:
            return "en-IN"
        return resp.json().get("language_code", "en-IN")


# ---------- Sarvam: translation ----------

async def translate_text(text: str, source: str, target: str) -> str:
    """Translate between English and Tamil using Sarvam."""
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


# ---------- Gemini: natural-language reasoning ----------

async def generate_reply(
    user_message: str,
    indicators: list,
    actions: list,
    explanation_level: str = "simple",
    is_followup: bool = False
) -> str:
    """Use Gemini to generate a natural cybersecurity reply."""
    if not gemini_client:
        print("[GEMINI] Client not initialized — key missing")
        return None

    if explanation_level == "simple":
        tone = (
            "Use simple, everyday language. Avoid technical jargon. "
            "Assume the user is not tech-savvy."
        )
    else:
        tone = (
            "You may use technical cybersecurity terms. "
            "Assume the user has some technical knowledge."
        )

    if indicators:
        context = (
            f"The user asked about a suspicious message.\n"
            f"Risk indicators detected by our rule engine: {indicators}\n"
            f"Required safety actions: {actions}\n"
            f"Explain these risks and actions naturally. Do not add new advice."
        )
    elif is_followup:
        context = (
            "The user described something vague. Ask 2-3 specific clarifying "
            "questions: what does the message say, does it ask for OTP/password/"
            "payment, does it ask to click a link."
        )
    else:
        context = (
            "The user asked a general cybersecurity question. "
            "Provide helpful general guidance."
        )

    prompt = f"""You are PolyCyGot, a multilingual cybersecurity assistant helping users identify phishing and scams.

{tone}

{context}

Rules:
- Keep the reply under 5 sentences.
- Never tell the user to share OTP, passwords, or click unknown links.
- Always recommend verifying through official channels.
- Do not make up facts about specific banks or companies.
- Speak directly to the user, in second person.

User message: {user_message}
"""

    try:
        response = await gemini_client.aio.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"[GEMINI ERROR] {type(e).__name__}: {e}")
        return None