import os
import httpx


SARVAM_API_URL = os.getenv(
    "SARVAM_API_URL",
    "https://api.sarvam.ai",
)


async def translate_text(
    text: str,
    source_language: str,
    target_language: str,
) -> str:

    api_key = os.getenv(
        "SARVAM_API_KEY"
    )

    if not api_key:
        return text

    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "input": text,
        "source_language_code": source_language,
        "target_language_code": target_language,
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{SARVAM_API_URL}/translate",
            headers=headers,
            json=payload,
        )

    if response.status_code != 200:
        return text

    data = response.json()

    return data.get(
        "translated_text",
        text,
    )