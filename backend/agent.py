from language_layer import detect_language, translate_text, generate_reply
from verifier import verify_recommendation

KEYWORDS = {
    "otp_request": ["otp", "one-time password", "verification code"],
    "urgent_threat": ["suspend", "block", "urgent", "immediately"],
    "suspicious_link": ["link", "click here", "verify now"],
    "credential_request": ["password", "pin", "cvv", "aadhaar"],
    "payment_request": ["payment", "transfer", "fee", "refund"],
}


async def process_message(
    message: str,
    language: str = "auto",
    explanation_level: str = "simple",
    session_id: str = None
) -> dict:
    # 1. Language detection
    detected = await detect_language(message)
    user_lang = detected if language == "auto" else language

    # 2. Normalize to English for Gemini
    if user_lang == "ta-IN":
        working_text = await translate_text(message, "ta-IN", "en-IN")
    else:
        working_text = message

    # 3. Detect indicators (for display only)
    indicators = []
    tl = working_text.lower()
    for rule_id, kws in KEYWORDS.items():
        if any(kw in tl for kw in kws):
            indicators.append({
                "rule_id": rule_id,
                "indicator": rule_id.replace("_", " ").title(),
                "risk": "high" if rule_id in ("otp_request", "credential_request") else "medium",
            })

    # 4. Let Gemini generate the reply
    english_reply = await generate_reply(
        user_message=working_text,
        explanation_level=explanation_level,
    )

    # 5. Safety check
    verification = verify_recommendation(english_reply or "", indicators)

    if verification["blocked_phrases"]:
        english_reply = (
            "I can't safely advise on that. Never share OTP, passwords, "
            "or click unknown links. Verify directly through your bank's "
            "official app or phone number."
        )
        verification = verify_recommendation(english_reply, indicators)

    # 6. Translate back if needed
    if user_lang == "ta-IN" and english_reply:
        final_reply = await translate_text(english_reply, "en-IN", "ta-IN")
    else:
        final_reply = english_reply or "I couldn't generate a response."

    return {
        "reply": final_reply,
        "detected_language": user_lang,
        "risk_indicators": indicators,
        "verification": verification,
        "needs_followup": False,
    }