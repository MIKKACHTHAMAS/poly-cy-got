import os

from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
except ImportError:
    genai = None


SYSTEM_PROMPT = """
You are PolyCyGot, a cybersecurity safety assistant.

Your job is to help users understand cybersecurity threats.

Never encourage:
- credential theft
- password theft
- OTP theft
- phishing
- malware deployment
- unauthorized access
- bypassing authentication
- evasion of security controls
- malicious exploitation

When a user asks about a suspicious message, explain:
1. What the threat indicators are.
2. Why the message may be suspicious.
3. What the user should do safely.

Give defensive and educational guidance.
"""


async def generate_response(message: str) -> str:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return (
            "Gemini API key is not configured. "
            "Please configure GEMINI_API_KEY."
        )

    if genai is None:
        return (
            "Google Gemini SDK is not installed."
        )

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
{SYSTEM_PROMPT}

User message:
{message}
"""

    response = client.models.generate_content(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        ),
        contents=prompt,
    )

    return response.text or ""