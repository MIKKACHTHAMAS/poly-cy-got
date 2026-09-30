from language_layer import detect_language, translate_text

# Simplified symbolic rules (MeTTa-inspired for MVP)
RISK_RULES = [
    {
        "id": "otp_request",
        "keywords": ["otp", "one time password", "verification code"],
        "indicator": "Message asks for OTP",
        "risk": "high",
        "action": "Never share OTP with anyone. Banks never ask for OTP."
    },
    {
        "id": "urgent_threat",
        "keywords": ["account suspend", "blocked", "urgent", "immediately", "within 24 hours"],
        "indicator": "Urgent threat creating pressure",
        "risk": "medium",
        "action": "Scammers create urgency to bypass your judgment."
    },
    {
        "id": "suspicious_link",
        "keywords": ["click here", "link", "verify now", "update account"],
        "indicator": "Unexpected link in message",
        "risk": "medium",
        "action": "Don't click links. Go to the official app or website directly."
    },
    {
        "id": "payment_request",
        "keywords": ["pay", "payment", "transfer", "fee", "charge"],
        "indicator": "Request for payment",
        "risk": "high",
        "action": "Legitimate banks don't demand immediate payment via message."
    }
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
    
    # 3. Apply symbolic rules
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
    needs_followup = len(indicators) == 0 and any(
        word in text_lower for word in ["message", "sms", "email", "link", "bank"]
    )
    
    # 5. Build English response
    if indicators:
        risk_summary = ", ".join([i["indicator"] for i in indicators])
        english_reply = (
            f"I found {len(indicators)} risk indicator(s): {risk_summary}. "
            f"What you should do: " + " ".join(actions) +
            " If you're unsure, verify directly through your bank's official app or phone number."
        )
    elif needs_followup:
        english_reply = (
            "I need more details to assess this. "
            "What exactly does the message say? "
            "Does it ask for OTP, password, payment, or ask you to click a link?"
        )
    else:
        english_reply = (
            "I don't see clear risk indicators in what you described. "
            "Can you share more details about the suspicious message?"
        )
    
    # 6. Translate back to user's language
    if user_lang == "ta-IN":
        final_reply = await translate_text(english_reply, "en-IN", "ta-IN")
    else:
        final_reply = english_reply
    
    return {
        "reply": final_reply,
        "detected_language": user_lang,
        "risk_indicators": indicators,
        "verification": {
            "status": "passed" if indicators else "insufficient_evidence",
            "checks": [{"rule": i["indicator"], "passed": True} for i in indicators]
        },
        "needs_followup": needs_followup
    }
