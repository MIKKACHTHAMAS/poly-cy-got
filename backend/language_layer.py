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
    """Detect language code using Sarvam, with short-input fallback."""
    stripped = text.strip()

    # Short English-looking input: skip Sarvam to avoid misclassification
    if len(stripped) < 10 and stripped.isascii():
        return "en-IN"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{SARVAM_BASE}/text-lid",
                json={"input": text},
                headers={"api-subscription-key": SARVAM_API_KEY}
            )
            if resp.status_code != 200:
                return "en-IN"
            return resp.json().get("language_code", "en-IN")
        except Exception:
            return "en-IN"


# ---------- Sarvam: translation ----------

async def translate_text(text: str, source: str, target: str) -> str:
    """Translate between English and Tamil using Sarvam."""
    if source == target:
        return text

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
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
        except Exception:
            return text


# ---------- Gemini: natural-language reasoning ----------

async def generate_reply(
    user_message: str,
    explanation_level: str = "simple",
) -> str:
    """Let Gemini decide everything — threat analysis, education, greetings."""
    if not gemini_client:
        print("[GEMINI] Client not initialized — key missing")
        return None

    if explanation_level == "simple":
        tone = (
            "Use simple, everyday language. Avoid technical jargon. "
            "Assume the user is not tech-savvy. Use relatable analogies."
        )
    else:
        tone = (
            "You may use technical cybersecurity terms. "
            "Assume the user has some technical knowledge."
        )

    prompt = f"""You are PolyCyGot, an adaptive multilingual cybersecurity assistant.

Your job is to help users with anything cybersecurity-related:
- If they describe a suspicious message, analyze the risks and advise them.
- If they ask "what is X?" (phishing, MFA, OTP, ransomware, etc.), explain it clearly with a relatable analogy.
- If they ask a general question, give helpful best practices.
- If they greet you, respond warmly and offer to help.
- If they're vague, ask 2-3 clarifying questions.

Tone: {tone}

Hard safety rules (never break these):
- Never tell the user to share an OTP, password, PIN, CVV, or Aadhaar number.
- Never tell the user to click a link from an unknown sender.
- Always recommend verifying through the sender's official app, website, or phone number.
- If unsure, err on the side of caution.

Keep replies under 6 sentences. Speak directly to the user in second person.

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