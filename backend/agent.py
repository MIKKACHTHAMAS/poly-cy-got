from language_layer import detect_language, translate_text, generate_reply
from verifier import verify_recommendation

RISK_RULES = [
    # ... keep your existing RISK_RULES list here ...
]


async def process_message(
    message: str,
    language: str = "auto",
    explanation_level: str = "simple",
    session_id: str = None
) -> dict:
    # 1. Language detection
    detected = await detect_language(message)
    user_lang = detected if language == "auto" else language

    # 2. Normalize to English for reasoning
    if user_lang == "ta-IN":
        working_text = await translate_text(message, "ta-IN", "en-IN")
    else:
        working_text = message

    # 3. Apply symbolic rules (unchanged)
    text_lower = working_text.lower()
    indicators = []
    actions = []

    for rule in RISK_RULES:
        if any(kw in text_lower for kw in rule["keywords"]):
            indicators.append({
                "rule_id": rule["id"],
                "indicator": rule["indicator"],
                "risk": rule["risk"]
            })
            actions.append(rule["action"])

    # 4. Determine if follow-up is needed
    question_words = ["how", "what", "why", "when", "where", "which", "can i", "should i", "explain"]
    is_question = any(q in text_lower for q in question_words) and "?" in working_text

    needs_followup = (
        len(indicators) == 0
        and not is_question
        and any(word in text_lower for word in ["message", "sms", "email", "link", "bank"])
    )

    # 5. Generate reply with LLM (NEW)
    english_reply = await generate_reply(
        user_message=working_text,
        indicators=[i["indicator"] for i in indicators],
        actions=actions,
        explanation_level=explanation_level,
        is_followup=needs_followup
    )
    print(f"[DEBUG] LLM returned: {english_reply!r}")
    # 6. Fallback if LLM fails (keeps agent working)
    if not english_reply:
        if indicators:
            risk_summary = ", ".join([i["indicator"] for i in indicators])
            english_reply = (
                f"I found {len(indicators)} risk indicator(s): {risk_summary}. "
                f"What you should do: " + " ".join(actions) +
                " Verify directly through your bank's official app or phone number."
            )
        elif needs_followup:
            english_reply = (
                "I need more details. What exactly does the message say? "
                "Does it ask for OTP, password, payment, or ask you to click a link?"
            )
        else:
            english_reply = (
                "I don't see clear risk indicators. Can you share more details?"
            )

    # 7. Verify the LLM's advice before showing it to the user
    verification = verify_recommendation(english_reply, indicators)

    if verification["status"] == "needs_review":
        # LLM tried to say something unsafe — override with safe fallback
        english_reply = (
            "I can't safely assess this message without more information. "
            "Do not share OTP, passwords, or click unknown links. "
            "Verify directly through your bank's official app or phone number."
        )
        verification = verify_recommendation(english_reply, indicators)

    # 8. Translate back to user's language
    if user_lang == "ta-IN":
        final_reply = await translate_text(english_reply, "en-IN", "ta-IN")
    else:
        final_reply = english_reply

    return {
        "reply": final_reply,
        "detected_language": user_lang,
        "risk_indicators": indicators,
        "verification": verification,
        "needs_followup": needs_followup
    }